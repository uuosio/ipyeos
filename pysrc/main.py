import sys
import asyncio
import atexit
import concurrent.futures
import signal
import time

from aiohttp import web
from ipyeos import eos, server
from IPython.terminal.embed import InteractiveShellEmbed

executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
queue = asyncio.Queue()

async def quit_app(request):
    eos.post(eos.quit)
    return web.Response(text="Done!\n"+ str(time.time()))

async def hello(request):
    def say_hello(name):
        print('hello', name)
        return name
    outputs = []
    for i in range(10):
        start = time.time()
        ret = eos.post(say_hello, 'alice')
        end = time.time()
        outputs.append(f"post test: {ret} diff: {int((end - start)*1e6)}")
    return web.Response(text='\n'.join(outputs))

async def run_ipython(request):
    await queue.put("ipython")
    return web.Response(text=f'done! {time.time()}')

async def start_webserver():
    app = web.Application()
    app.router.add_get('/ipython', run_ipython)
    app.router.add_get('/quit', quit_app)
    app.router.add_get('/', hello)
    runner = web.AppRunner(app)
    await runner.setup()
    try:
        site = web.TCPSite(runner, 'localhost', 7777)
    except Exception as e:
        print(e)
        site = web.TCPSite(runner, 'localhost', 7778)
    await site.start()
    print('++++++++++++server started!!')
    while True:
        await asyncio.sleep(3600) # serve forever

def run():
    if sys.argv[1] == 'eosnode':
        async def run_eos():
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
            future = asyncio.get_event_loop().run_in_executor(executor, _run_eos)
            await future
            await queue.put(None)

        def _run_ipython():
            shell = InteractiveShellEmbed(header="Starting IPython console in thread", colors="Neutral", banner1="")
            shell()
            atexit.unregister(shell.atexit_operations)
            shell.history_manager.end_session()
            shell.history_manager.writeout_cache()

        async def set_warn_level():
            await asyncio.sleep(10.0)
            print('set default log level to warn')
            eos.post(eos.set_warn_level, 'default')

        async def main():
            asyncio.create_task(start_webserver())
            asyncio.create_task(run_eos())
            asyncio.create_task(set_warn_level())

            while True:
                command = await queue.get()
                if not command:
                    break
                if command == 'ipython':
                    future = asyncio.get_event_loop().run_in_executor(executor, _run_ipython)

            # result = await future
            # print("Result: ", result)
            print('all done!')
        asyncio.run(main())
    elif sys.argv[1] == 'eosdebugger':
        result, unknown = parser.parse_known_args()
        server.start_debug_server(result.addr, result.server_port, result.vm_api_port, result.apply_request_addr, result.apply_request_port, result.addr,result.rpc_server_port)                
    else:
        parser.print_help()
