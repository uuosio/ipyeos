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
import yaml

from aiohttp import web
from multiprocessing import Process, Lock, Queue, Event
from typing import Optional

from . import args, debug_server, eos, helper, log, node, rpc, server, worker
from .debug import get_free_port

if not 'RUN_IPYEOS' in os.environ:
    print('main module can only be load by ipyeos')
    sys.exit(0)

logger = log.get_logger(__name__)

def print_help():
    return eos.init(['ipyeos', '--help'])

class Main(object):
    def __init__(self, node_type='pyeosnode'):
        self.node_type = node_type
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

    def start_webserver(self, quit_app):
        server = debug_server.init(quit_app)
        self.debug_server_task = asyncio.create_task(debug_server.start(server))
        self.debug_server = server

        server = rpc.init()
        self.rpc_server_task = asyncio.create_task(rpc.start(server))
        self.rpc_server = server

    def shutdown_worker_processes(self):
        for worker in self.worker_processes:
            p, msg, exit_event = worker
            exit_event.set() # shutdown worker

    async def shutdown_webserver(self):
        if not self.debug_server_task:
            return

        self.debug_server.exit()
        self.rpc_server.exit()

        await self.debug_server_task
        await self.rpc_server_task

        self.debug_server_task = None
        self.debug_server = None

        self.rpc_server_task = None
        self.rpc_server = None

    def _init_eos(self):
        argv = sys.argv[1:]
        argv[0] = 'ipyeos'
        ret = eos.init(argv)
        if not ret == 0:
            print('init return', ret)
            return False
        return True

    def _run_eos(self):
        ret = eos.run()
        # while True:
        #     ret = eos.run_once()
        #     if not ret == 0:
        #         break
        #     await asyncio.sleep(0.0)
        #     print('run once')
        print('run return', ret)
        return ret

    async def exec_code(self, request):
        data = await request.post()
        try:
            code = data['code']
            logger.info('exec code:\n %s', code)
            exec(code)
            return web.Response(text='OK')
        except Exception as e:
            exception_str = traceback.format_exc()
            logger.error('exec code error:\n %s', exception_str)
            return web.Response(text=exception_str)

    async def shutdown(self):
        if self.in_shutdown:
            logger.info("+++++++already in shutdown...")
            return

        self.in_shutdown = True

        logger.info("+++++++shutdown...")
        self.shutdown_worker_processes()

        if self.node_type == 'eosnode':
            logger.info("quit eosnode")
            eos.quit()
            # eos.post(eos.quit)

        eos.exit()
        
        logger.info('shutdown webserver')
        await self.shutdown_webserver()

        loop = asyncio.get_running_loop()
        tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
        # tasks = [t for t in asyncio.all_tasks(loop)]
        for task in tasks:
            logger.info('wait for task: %s', task)
            # try:
            #     await asyncio.wait_for(task, 1.0)
            # except asyncio.exceptions.TimeoutError:
            #     task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        # loop.stop()
        logger.info('shutdown done')

    def quit_node(self):
        asyncio.create_task(self.shutdown())

    def start_worker_processes(self, worker_processes, config_file, genesis_file='', snapshot_file=''):
        if not worker_processes:
            return True
        self.worker_processes = []
        self.rwlock = worker.ReadWriteLock()
        for port in worker_processes:
            in_queue, out_queue = Queue(), Queue()
            exit_event = Event()
            messenger = worker.Messenger(in_queue, out_queue)
            logger.info('start worker %s', port)
            p = Process(target=worker.run, args=(port, self.rwlock, worker.Messenger(out_queue, in_queue), exit_event, config_file, genesis_file, snapshot_file))
            p.start()
            ret = messenger.get()
            if not ret:
                logger.error('worker %s start failed', port)
                return False
            logger.info('worker %s started', port)
            self.worker_processes.append((p, messenger, exit_event))

            def message_listener(messenger):
                while True:
                    try:
                        msg = messenger.get()
                        if not msg:
                            break
                        logger.info('worker %s message: %s', port, msg)
                        if msg == 'get_info':
                            msg = node.get_node().api.get_info(is_json=False)
                            messenger.put(msg)
                            logger.info('worker %s message: %s', port, msg)
                    except Exception as e:
                        logger.error('message_listener error: %s', e)
                        break
            threading.Thread(target=message_listener, args=(messenger, )).start()
        return True

    def handle_signal(self, signum):
        logger.info("handle_signal: %s", signum)
        self.quit_node()

    async def main_eosnode(self):
        if not self._init_eos():
            return
        self.start_webserver(self.quit_node)
        self.async_queue = asyncio.Queue()
        future = asyncio.get_event_loop().run_in_executor(self.executor, self._run_eos)
        try:
            await future
        except asyncio.exceptions.CancelledError:
            logger.info('asyncio.exceptions.CancelledError')

        await self.shutdown()
        print('all done!')

    async def main_pyeosnode(self):
        result = args.parse_args()
        _node = node.init_node(result.config_file, result.genesis_file, result.snapshot_file)
        try:
            worker_processes = _node.config['worker_processes']
            if not self.start_worker_processes(worker_processes, result.config_file, result.genesis_file, result.snapshot_file):
                await self.shutdown()
                return False
        except KeyError:
            logger.info('+++++no worker_process_num in config file')
            pass

        self.start_webserver(self.quit_node)

        await node.start_network(self.rwlock)
        await self.shutdown()
        # await asyncio.sleep(0.5)
        print('all done!')

    async def main(self):
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, self.handle_signal, signal.SIGINT)
        loop.add_signal_handler(signal.SIGTERM, self.handle_signal, signal.SIGTERM)

        if self.node_type == 'eosnode':
            return await self.main_eosnode()
        elif self.node_type == 'pyeosnode':
            return await self.main_pyeosnode()
        assert False, 'unknown node type'

def run_eosnode():
    if len(sys.argv) <= 2 or sys.argv[2] in ['-h', '--help']:
        return print_help()

    m = Main('eosnode')
    try:
        asyncio.run(m.main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")

def run_pyeosnode():
    m = Main('pyeosnode')
    try:
        asyncio.run(m.main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt")

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
