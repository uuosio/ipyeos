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
from typing import Optional

import yaml
from aiohttp import web

from . import args, debug_server, eos, helper, log, node, rpc, server
from .debug import get_free_port

if not 'RUN_IPYEOS' in os.environ:
    print('main module can only be load by ipyeos')
    sys.exit(0)

logger = log.get_logger(__name__)

def print_help(self):
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

    def start_webserver(self, quit_app):
        server = debug_server.init(quit_app)
        self.debug_server_task = asyncio.create_task(debug_server.start(server))
        self.debug_server = server

        server = rpc.init()
        self.rpc_server_task = asyncio.create_task(rpc.start(server))
        self.rpc_server = server

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

    def _run_eos(self):
        argv = sys.argv[1:]
        argv[0] = 'ipyeos'
        ret = eos.init(argv)
        if not ret == 0:
            print('init return', ret)
            return
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

        if self.node_type == 'eosnode':
            logger.info("quit eosnode")
            eos.quit()
            # eos.post(eos.quit)

        logger.info('shutdown webserver')
        await self.shutdown_webserver()

        loop = asyncio.get_running_loop()
        tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
        # tasks = [t for t in asyncio.all_tasks(loop)]
        for task in tasks:
            logger.info('cancle task: %s', task)
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()

    def quit_node(self):
        asyncio.create_task(self.shutdown())

    def handle_signal(self, signum, loop):
        logger.info("handle_signal: %s", signum)
        self.quit_node()

    async def main_eosnode(self):
        self.async_queue = asyncio.Queue()
        future = asyncio.get_event_loop().run_in_executor(self.executor, self._run_eos)
        try:
            await future
        except asyncio.exceptions.CancelledError:
            logger.info('asyncio.exceptions.CancelledError')
        print('all done!')

    async def main_pyeosnode(self):
        result = args.parse_args()
        await node.start(result.config_file, result.genesis_file, result.snapshot_file)

        await self.shutdown_webserver()

        print('all done!')

    async def main(self):
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, self.handle_signal, signal.SIGINT, loop)
        loop.add_signal_handler(signal.SIGTERM, self.handle_signal, signal.SIGTERM, loop)

        self.start_webserver(self.quit_node)

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
