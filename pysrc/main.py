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

from aiohttp import web
from IPython.terminal.embed import InteractiveShellEmbed

from . import eos, server
from . import args
from . import node
from . import log

if not 'RUN_IPYEOS' in os.environ:
    print('main module can only be load by ipyeos')
    sys.exit(0)

logger = log.get_logger(__name__)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
async_queue = asyncio.Queue()

thread_queue = queue.Queue()

async def quit_app(request):
    eos.post(eos.quit)
    return web.Response(text="Done!\n"+ str(time.time()))

async def hello(request):
    commands = '''
commands:
/ipython start ipython
/ikernel start ikernel
/quit quit app
    '''
    return web.Response(text=commands)

def print_help():
    return eos.init(['ipyeos', '--help'])

def _run_eos():
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

async def run_eos():
    future = asyncio.get_event_loop().run_in_executor(executor, _run_eos)
    await future
    await async_queue.put(None)


def _run_ipython():
    from . import ipython_embed
    shell = ipython_embed.embed()
    atexit.unregister(shell.atexit_operations)
    shell.atexit_operations()

async def run_ipython(request):
    # await async_queue.put("ipython")
    # thread_queue.put("ipython")
    future = asyncio.get_event_loop().run_in_executor(executor, _run_ipython)
    return web.Response(text=f'done! {time.time()}')

def _run_ikernel():
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)

    from . import ipykernel_embed
    ipykernel_embed.embed_kernel(ip='0.0.0.0')

async def run_ikernel(request):
    # await async_queue.put("ikernel")
    # thread_queue.put("ikernel")
    future = asyncio.get_event_loop().run_in_executor(executor, _run_ikernel)
    return web.Response(text=f'done! {time.time()}')

async def set_warn_level():
    await asyncio.sleep(3.0)
    eos.post(eos.set_info_level, 'default')
    print('set default log level to warn')

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

async def start_webserver():
    app = web.Application()
    app.router.add_get('/ipython', run_ipython)
    app.router.add_get('/ikernel', run_ikernel)
    app.router.add_get('/quit', quit_app)
    app.router.add_get('/', hello)
    runner = web.AppRunner(app)
    await runner.setup()

    for i in range(10):
        port = 7777 + i
        if is_port_in_use(port):
            continue
        site = web.TCPSite(runner, host='127.0.0.1', port=port)
        await site.start()
        logger.info(f'++++++++++++debugging server started at port {port}!!')
        break

    while True:
        await asyncio.sleep(3600) # serve forever

async def heartbeat():
    while True:
        print("beep")
        await asyncio.sleep(5.0)

async def main():
    asyncio.create_task(start_webserver())
    asyncio.create_task(run_eos())
    asyncio.create_task(set_warn_level())
    # asyncio.create_task(heartbeat())

    while True:
        command = await async_queue.get()
        if not command:
            break
        if command == 'ipython':
            # _run_ipython()
            future = asyncio.get_event_loop().run_in_executor(executor, _run_ipython)
        elif command == 'ikernel':
            _run_ikernel()
            # future = asyncio.get_event_loop().run_in_executor(executor, _run_ipython)

    # result = await future
    # print("Result: ", result)
    print('all done!')

def run_eosnode():
    if len(sys.argv) <= 2 or sys.argv[2] in ['-h', '--help']:
        return print_help()

    def start():
        asyncio.run(main())
        thread_queue.put(None)
    t = threading.Thread(target=start, daemon=True)
    t.start()
    while True:
        try:
            cmd = thread_queue.get()
            if cmd == None:
                break
            if cmd == 'ikernel':
                _run_ikernel()
            elif cmd == 'ipython':
                _run_ipython()
        except KeyboardInterrupt:
            eos.post(eos.quit)


async def pyeosnode_main():
    result = args.parse_args()
    asyncio.create_task(start_webserver())
    asyncio.create_task(node.start(result.config_file, result.genesis_file, result.snapshot_file))
    while True:
        try:
            await asyncio.sleep(3600)
        except asyncio.exceptions.CancelledError:
            logger.info('main task cancelled')
            break
    print('all done!')

def run_pyeosnode():
    try:
        asyncio.run(pyeosnode_main())
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
