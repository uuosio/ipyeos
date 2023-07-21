import asyncio
import atexit
import concurrent.futures
import time
import traceback

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from . import exec_result, helper, log
from . import node_config
from .uvicorn_server import UvicornServer

logger = log.get_logger(__name__)

app = FastAPI()

quit_app = None

class Item(BaseModel):
    code: str

def _run_ipython():
    from . import ipython_embed
    shell = ipython_embed.embed()
    atexit.unregister(shell.atexit_operations)
    shell.atexit_operations()

def _run_ikernel():
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)

    from . import ipykernel_embed
    ipykernel_embed.embed_kernel(ip='0.0.0.0')

@app.get("/", response_class=HTMLResponse)
async def root():
    return helper.html

executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

@app.get("/ipython")
async def run_ipython():
    future = asyncio.get_event_loop().run_in_executor(executor, _run_ipython)
    return f"Done! {time.time()}"

@app.get("/ikernel")
async def run_ikernel():
    future = asyncio.get_event_loop().run_in_executor(executor, _run_ikernel)
    return f"Done! {time.time()}"

@app.post("/exec")
async def exec_code(item: Item):
    try:
        # logger.info('exec code:\n %s', code)
        exec(item.code)
        return exec_result.get()
    except Exception as e:
        exception_str = traceback.format_exc()
        # logger.error('exec code error:\n %s', exception_str)
        return dict(text=exception_str)

@app.get("/quit")
@app.post("/quit")
async def quit():
    global quit_app
    if quit_app:
        quit_app()
    return f"Done! {time.time()}"

def init(quit):
    global quit_app
    quit_app = quit

    try:
        port = node_config.get_config()['debug_port']
    except KeyError:
        port = 7777
    except AssertionError:
        port = 7777

    logger.info('start debug webserver at port %s', port)
    config = uvicorn.Config(app, host="127.0.0.1", port=port)
    server = UvicornServer(config)
    return server

async def start(server):
    try:
        await server.serve()
    except asyncio.exceptions.CancelledError:
        logger.info('debug webserver stopped')

if __name__ == '__main__':
    asyncio.run(start(None))
