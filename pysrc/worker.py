import multiprocessing
from . import node

import asyncio
import json
import uvicorn
import threading

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from .uvicorn_server import UvicornServer
from . import log, net, node
from .chain_exceptions import BlockValidateException, ChainException

logger = log.get_logger(__name__)

app = FastAPI()


class Item(BaseModel):
    code: str

class PushReadOnlyTransactionArgs(BaseModel):
    """
    A Pydantic model that represents the arguments for the `push_ro_transaction` RPC method.

    Attributes:
        packed_tx: A hex string that contains the packed transaction data.
        Related C++ struct:
        ```C++
        struct packed_transaction : fc::reflect_init {
        private:
            vector<signature_type>                  signatures;
            fc::enum_type<uint8_t,compression_type> compression;
            bytes                                   packed_context_free_data;
            // transaction (not signed_transaction) packed and possibly compressed according to compression
            bytes                                   packed_trx;
        };
        ```
    """
    packed_tx: str

class Messenger(object):
    def __init__(self, in_queue, out_queue):
        self.in_queue = in_queue
        self.out_queue = out_queue

    def get(self, wait=True):
        return self.in_queue.get(wait)

    def get_nowait(self):
        return self.in_queue.get_nowait()

    def put(self, data):
        self.out_queue.put(data)

async def read_root():
    """
    Returns a JSON object with a single key-value pair: "Hello" -> "World".
    """
    return {"Hello": "World"}

@app.get("/get_info", response_class=PlainTextResponse)
async def get_info():
    g_worker.messenger.put('get_info')
    logger.info('get_info')
    try:
        msg = g_worker.messenger.get()
        logger.info('get_info: %s', msg)
        return msg
    except Exception as e:
        logger.exception(e)
    return 'None'
    # return node.get_node().api.get_info(is_json=False)

@app.post("/push_ro_transaction", response_class=PlainTextResponse)
async def push_ro_transaction(args: PushReadOnlyTransactionArgs):
    packed_tx = bytes.fromhex(args.packed_tx)
    return node.get_node().chain.push_ro_transaction(packed_tx, return_json=False)

g_worker = None

class Worker(object):
    def __init__(self, messenger: Messenger, exit_event, port: int=8089):
        app.get("/")(read_root)
        self.config = uvicorn.Config(app, host="127.0.0.1", port=port)
        self.server = UvicornServer(self.config)
        self.should_exit = False

        self.messenger = messenger
        self.exit_event = exit_event

    async def start(self):
        try:
            await self.server.serve()
        except asyncio.exceptions.CancelledError:
            logger.info('worker: asyncio.exceptions.CancelledError')

    async def main(self):
        asyncio.create_task(self.start())
        while not self.should_exit:
            await asyncio.sleep(0.1)

    def exit_listener(self):
        self.exit_event.wait()
        self.should_exit = True
        self.messenger.put(None)
        logger.info('exit_listener')

def run(port, database_write_lock: multiprocessing.Lock, messenger: Messenger, exit_event, config_file, genesis_file, snapshot_file):
    global g_worker
    _node = node.init_node(config_file, genesis_file, snapshot_file, worker_process=True)
    _node.chain.start_block()
    messenger.put('init done')

    g_worker = Worker(messenger, exit_event, port)
    threading.Thread(target=g_worker.exit_listener).start()

    try:
        logger.info('worker process starting...')
        asyncio.run(g_worker.main())
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt')