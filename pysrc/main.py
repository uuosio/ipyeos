import argparse
import asyncio
import concurrent.futures
import os
import queue
import signal
import socket
import sys
import threading
import time
import traceback
import uvloop
import yaml

from multiprocessing import Process, Lock, Queue, Event
from typing import Optional

from . import args, debug, debug_server, eos, helper, log, node, node_config, rpc, server, worker, utils
from .chain_exceptions import ChainException

if not 'RUN_IPYEOS' in os.environ:
    print('only ipyeos can load the main module.')
    sys.exit(0)

logger = log.get_logger(__name__)

def print_help():
    return eos.init(['ipyeos', '--help'])

class Main(object):
    def __init__(self, node_type='pyeosnode'):
        self.node_type = node_type
        eos.set_node_type(node_type)

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        self.thread_queue = queue.Queue()
        self.async_queue: Optional[asyncio.Queue()] = None
        self.in_shutdown = False

        self.debug_server_task = None
        self.debug_server = None

        self.rpc_server_task = None
        self.rpc_server = None

        self.worker_processes = []
        self.rwlock = None
        self.init_finished_event = threading.Event()
        self.init_worker_process_finished_event = None

        self.init_success = False

    def start_webserver(self, quit_app):
        server = debug_server.init(quit_app)
        if not server:
            return False

        try:
            port = node_config.get_config()['debug_port']
        except KeyError:
            port = 7777
        except AssertionError:
            port = 7777

        if not utils.can_listen(f'127.0.0.1:{port}'):
            logger.error('debug_port %s is in use', port)
            return False

        self.debug_server_task = asyncio.create_task(debug_server.start(server))
        self.debug_server = server

        if self.node_type == 'eosnode':
            return True

        try:
            rpc_address = node_config.get_config()['rpc_address']
        except:
            rpc_address = '127.0.0.1:8088'
            logger.info('+++++no rpc_address in config file, use default: %s', rpc_address)
        server = rpc.init(rpc_address)
        if not server:
            return False
        self.rpc_server_task = asyncio.create_task(rpc.start(server))
        self.rpc_server = server
        return True

    def shutdown_worker_processes(self):
        for worker in self.worker_processes:
            p, msg, exit_event = worker
            exit_event.set() # shutdown worker
            p.join()

    async def shutdown_webserver(self):
        if not self.debug_server_task:
            return

        if self.debug_server:
            self.debug_server.exit()
            await self.debug_server_task
            self.debug_server_task = None
            self.debug_server = None

        if self.rpc_server:
            self.rpc_server.exit()
            await self.rpc_server_task
            self.rpc_server_task = None
            self.rpc_server = None

    def _init_eos(self, genesis_file, snapshot_file):
        config = node_config.get_config()
        argv = ['ipyeos']
        for key in config:
            if key in ('worker_processes', 'debug_port', 'rpc_address'):
                continue
            value = config[key]
            if value is None:
                argv.append('--'+key.replace('_', '-'))
            else:
                if key == 'plugin':
                    for v in value:
                        argv.append('--plugin'+'='+str(v))
                else:
                    argv.append('--'+key.replace('_', '-')+'='+str(value))

        if genesis_file:
            argv.append('--genesis-json='+genesis_file)

        if snapshot_file:
            argv.append('--snapshot='+snapshot_file)
        logger.info(' '.join(argv))
        ret = eos.init(argv)
        if not ret == 0:
            logger.info('init return %s', ret)
            return False
        return True

    def _run_eos(self, genesis_file, snapshot_file):
        logger.info('run_eos %s %s', genesis_file, snapshot_file)
        try:
            self.init_success = self._init_eos(genesis_file, snapshot_file)
            logger.info('_init_eos return: %s', self.init_success)
            if not self.init_success:
                eos.exit()
                self.init_finished_event.set()
                self.init_success = False
                return False

            node.attach_node()

            try:
                worker_processes = node_config.get_config()['worker_processes']
                if not self.start_worker_processes(worker_processes):
                    eos.exit()
                    self.init_finished_event.set()
                    self.init_success = False
                    return False
            except KeyError:
                logger.info('+++++no worker_process_num in config file')
            self.init_finished_event.set()

        except Exception as e:
            logger.exception(e)
            self.init_success = False
            self.init_finished_event.set()
            return False
        logger.info('+++++eos.run')
        ret = eos.run()
        # while True:
        #     ret = eos.run_once()
        #     if not ret == 0:
        #         break
        #     await asyncio.sleep(0.0)
        #     print('run once')
        eos.exit()
        logger.info('run return %s', ret)
        if ret == 0:
            return True
        return False

    async def shutdown(self):
        if self.in_shutdown:
            logger.info("+++++++already in shutdown...")
            return

        self.in_shutdown = True

        logger.info("+++++++shutdown...")
        self.shutdown_worker_processes()

        # eos.post(eos.quit)
        
        logger.info('shutdown webserver')
        await self.shutdown_webserver()

        loop = asyncio.get_running_loop()
        tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
        # tasks = [t for t in asyncio.all_tasks(loop)]
        for task in tasks:
            logger.info('wait for task: %s', task)
            try:
                await asyncio.wait_for(task, 3.0)
            except asyncio.exceptions.TimeoutError:
                logger.info('task %s timeout, cancel it', task)
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        # loop.stop()
        logger.info('shutdown done')

    def quit_node(self):
        if self.node_type == 'eosnode':
            logger.info("quit eosnode")
            eos.quit()
        eos.exit()
        # asyncio.create_task(self.shutdown())

    def start_worker_processes(self, worker_processes):
        if not worker_processes:
            return True
        self.worker_processes = []
        self.rwlock = worker.ReadWriteLock()

        data_dir = eos.data_dir()
        config_dir = eos.config_dir()
        if self.node_type == 'eosnode':
            state_size = int(eos.get_chain_config()['state_size'])
        else:
            state_size = int(node.get_node().chain.get_chain_config()['state_size'])

        for rpc_address in worker_processes:
            if not utils.can_listen(rpc_address):
                logger.error('rpc_address %s is in use', rpc_address)
                return False
            in_queue, out_queue = Queue(), Queue()
            exit_event = Event()
            messenger = worker.Messenger(in_queue, out_queue)
            logger.info('start worker %s', rpc_address)
            p = Process(target=worker.run, args=(rpc_address, self.rwlock, worker.Messenger(out_queue, in_queue), exit_event, data_dir, config_dir, state_size))
            p.start()
            ret = messenger.get_timeout(3.0)
            if not ret:
                logger.error('worker %s start failed', rpc_address)
                return False
            logger.info('worker %s started', rpc_address)
            self.worker_processes.append((p, messenger, exit_event))

            def message_listener(messenger):
                while True:
                    try:
                        msg = messenger.get()
                        if not msg:
                            break
                        logger.info('worker %s message: %s', rpc_address, msg)
                        if msg == 'get_info':
                            msg = node.get_node().api.get_info(is_json=False)
                            messenger.put(msg)
                            logger.info('worker %s message: %s', rpc_address, msg)
                    except Exception as e:
                        logger.error('message_listener error: %s', e)
                        messenger.put(str(e))
            threading.Thread(target=message_listener, args=(messenger, )).start()
        return True

    def handle_signal(self, signum):
        logger.info("handle_signal: %s", signum)
        self.quit_node()

    async def main_eosnode(self):
        result = args.parse_args()
        node_config.load_config(result.config_file)

        self.async_queue = asyncio.Queue()
        future = asyncio.get_event_loop().run_in_executor(self.executor, self._run_eos, result.genesis_file, result.snapshot_file)

        self.init_finished_event.wait()
        if not self.init_success:
            return False

        if not self.start_webserver(self.quit_node):
            await self.shutdown()
            return False

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, self.handle_signal, signal.SIGINT)
        loop.add_signal_handler(signal.SIGTERM, self.handle_signal, signal.SIGTERM)

        # while not eos.should_exit():
        #     await asyncio.sleep(0.2)
        try:
            await future
        except asyncio.exceptions.CancelledError:
            logger.info('asyncio.exceptions.CancelledError')
        logger.info('++++++++run_eos done!')
        await self.shutdown()
        logger.info('all done!')

    async def main_pyeosnode(self):
        result = args.parse_args()
        if not os.path.exists(result.config_file):
            logger.error('config file not exists: %s', result.config_file)
            return False

        if result.genesis_file and not os.path.exists(result.genesis_file):
            logger.error('genesis file not exists: %s', result.genesis_file)
            return False

        if result.snapshot_file and not os.path.exists(result.snapshot_file):
            logger.error('snapshot file not exists: %s', result.snapshot_file)
            return False

        try:
            node.init_node(result.config_file, result.genesis_file, result.snapshot_file, self.rwlock)
        except ChainException as e:
            logger.exception(e)
            return False

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, self.handle_signal, signal.SIGINT)
        loop.add_signal_handler(signal.SIGTERM, self.handle_signal, signal.SIGTERM)

        try:
            worker_processes = node_config.get_config()['worker_processes']
            if not self.start_worker_processes(worker_processes):
                self.quit_node()
                await self.shutdown()
                return False
        except KeyError:
            logger.info('+++++no worker_process_num in config file')
            pass

        if not self.start_webserver(self.quit_node):
            await self.shutdown()
            return False

        await node.start_network()
        await self.shutdown()
        # await asyncio.sleep(0.5)
        print('all done!')

    async def main(self):

        import asyncio
        import aiomonitor

        loop = asyncio.get_event_loop()
        with aiomonitor.start_monitor(loop):
            logger.info("Now you can connect with: nc localhost 50101 or rlwrap nc localhost 50101")
            if self.node_type == 'eosnode':
                return await self.main_eosnode()
            elif self.node_type == 'pyeosnode':
                return await self.main_pyeosnode()
            assert False, 'unknown node type'

def run_node(m: Main):
    if sys.version_info >= (3, 11):
        with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
            try:
                runner.run(m.main())
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt")
    else:
        uvloop.install()
        try:
            asyncio.run(m.main())
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")

def run_eosnode():
    if len(sys.argv) <= 2 or sys.argv[2] in ['-h', '--help']:
        return print_help()

    m = Main('eosnode')
    run_node(m)

def run_pyeosnode():
    m = Main('pyeosnode')
    run_node(m)

def run():
    if sys.argv[1] == 'eosnode':
        return run_eosnode()
    elif sys.argv[1] == 'pyeosnode':
        return run_pyeosnode()
    else:
        result = args.parse_args()
        if result.subparser == 'eosdebugger':
            server.start_debug_server(result.addr, result.server_port, result.vm_api_port, result.apply_request_addr, result.apply_request_port, result.addr,result.rpc_server_port)
        else:
            parser.print_help()
