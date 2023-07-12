import os
import argparse
import asyncio
import atexit
import concurrent.futures
import queue
import yaml
import signal
import sys
import socket
import time
import threading
import traceback
from typing import Optional

from aiohttp import web
from . import eos, server
from . import args
from . import helper
from . import log
from . import node
from .debug import get_free_port
from . import rpc
from . import debug_server

if not 'RUN_IPYEOS' in os.environ:
    print('main module can only be load by ipyeos')
    sys.exit(0)

logger = log.get_logger(__name__)

def print_help(self):
    return eos.init(['ipyeos', '--help'])

class Main(object):
    def __init__(self):
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

    def quit_eosnode(self, request):
        eos.post(eos.quit)

    def quit_pyeosnode(self):
        asyncio.create_task(self.shutdown())

    async def show_commands(self, request):
        return web.Response(text=helper.html, content_type='text/html')

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

    async def run_eos(self):
        future = asyncio.get_event_loop().run_in_executor(self.executor, self._run_eos)
        await future
        logger.info('eosnode exit')
        await self.async_queue.put(None)

    def _run_ipython(self):
        from . import ipython_embed
        shell = ipython_embed.embed()
        atexit.unregister(shell.atexit_operations)
        shell.atexit_operations()

    async def run_ipython(self, request):
        # await async_queue.put("ipython")
        # thread_queue.put("ipython")
        future = asyncio.get_event_loop().run_in_executor(self.executor, self._run_ipython)
        return web.Response(text=f"Done!\n{str(time.time())}\n")

    def _run_ikernel(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)

        from . import ipykernel_embed
        ipykernel_embed.embed_kernel(ip='0.0.0.0')

    async def run_ikernel(self, request):
        # await async_queue.put("ikernel")
        # thread_queue.put("ikernel")
        future = asyncio.get_event_loop().run_in_executor(self.executor, self._run_ikernel)
        return web.Response(text=f"Done!\n{str(time.time())}\n")

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


    async def main_eosnode(self):
        self.async_queue = asyncio.Queue()
        self.start_webserver(self.quit_eosnode)
        asyncio.create_task(self.run_eos())

        while True:
            # await asyncio.sleep(10.0)
            # continue
            command = await self.async_queue.get()
            if not command:
                break
            if command == 'ipython':
                # _run_ipython()
                future = asyncio.get_event_loop().run_in_executor(self.executor, self._run_ipython)
            elif command == 'ikernel':
                self._run_ikernel()
                # future = asyncio.get_event_loop().run_in_executor(executor, _run_ipython)

        # result = await future
        # print("Result: ", result)
        print('all done!')

    async def shutdown(self):
        if self.in_shutdown:
            logger.info("+++++++already in shutdown...")
            return

        self.in_shutdown = True

        logger.info("+++++++shutdown...")

        await self.shutdown_webserver()

        loop = asyncio.get_running_loop()
        tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
        # tasks = [t for t in asyncio.all_tasks(loop)]
        for task in tasks:
            logger.info('cancle task: %s', task)
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()

    def handle_signal(self, signum, loop):
        logger.info("+++++++handle signal: %s, shutting down...", signum)
        loop.create_task(self.shutdown())
        return

    async def pyeosnode_main(self):
        loop = asyncio.get_running_loop()

        self.start_webserver(self.quit_pyeosnode)

        loop.add_signal_handler(signal.SIGINT, self.handle_signal, signal.SIGINT, loop)
        loop.add_signal_handler(signal.SIGTERM, self.handle_signal, signal.SIGTERM, loop)

        result = args.parse_args()
        await node.start(result.config_file, result.genesis_file, result.snapshot_file)

        await self.shutdown_webserver()

        print('all done!')

def run_eosnode():
    if len(sys.argv) <= 2 or sys.argv[2] in ['-h', '--help']:
        return print_help()

    m = Main()
    def start():
        asyncio.run(m.main_eosnode())
        m.thread_queue.put(None)
    t = threading.Thread(target=start, daemon=True)
    t.start()
    while True:
        try:
            cmd = m.thread_queue.get()
            if cmd == None:
                break
            if cmd == 'ikernel':
                m._run_ikernel()
            elif cmd == 'ipython':
                m._run_ipython()
        except KeyboardInterrupt:
            eos.post(eos.quit)

def run_pyeosnode():
    m = Main()
    try:
        asyncio.run(m.pyeosnode_main())
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
