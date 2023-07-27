import asyncio
import json
import logging
import signal
import sys
import uvicorn
import uvloop
import threading
import time

from aiocache import cached, Cache
from aiocache.serializers import StringSerializer

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from multiprocessing import Process, Condition, Value, Lock, Event

from .uvicorn_server import UvicornServer
from . import eos, log, net, node, rate_limit
from .chain_exceptions import BlockValidateException, DatabaseGuardException, ChainException

logger = log.get_logger(__name__)

app = FastAPI()

logging.getLogger('uvicorn').setLevel(logging.WARNING)
logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
logging.getLogger('fastapi').setLevel(logging.WARNING)

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

    def get_timeout(self, timeout):
        while timeout > 0:
            if self.in_queue.empty():
                time.sleep(0.1)
                timeout -= 0.1
                continue
            return self.in_queue.get_nowait()
        return None

    def put(self, data):
        self.out_queue.put(data)

class ReadWriteLock:
    class _RLock:
        def __init__(self, lock):
            self._lock = lock

        def __enter__(self):
            self._lock._read_ready.acquire()
            self._lock._readers.value += 1
            self._lock._read_ready.release()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._lock._read_ready.acquire()
            self._lock._readers.value -= 1
            if not self._lock._readers.value:
                self._lock._read_ready.notify_all()
            self._lock._read_ready.release()

    class _WLock:
        def __init__(self, lock):
            self._lock = lock

        def __enter__(self):
            self._lock._read_ready.acquire()
            while self._lock._readers.value > 0:
                self._lock._read_ready.wait()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._lock._read_ready.notify_all()
            self._lock._read_ready.release()

    def __init__(self):
        self._read_ready = Condition(Lock())
        self._readers = Value('i', 0)  # integer, initially 0

    def rlock(self):
        return self._RLock(self)

    def wlock(self):
        return self._WLock(self)

g_worker = None

async def read_root():
    """
    Returns a JSON object with a single key-value pair: "Hello" -> "World".
    """
    return {"Hello": "World"}

@app.get("/v1/chain/get_info", response_class=PlainTextResponse)
@cached(ttl=1, cache=Cache.MEMORY, key="get_info", serializer=StringSerializer())
async def get_info():
    g_worker.messenger.put('get_info')
    try:
        msg = g_worker.messenger.get()
        logger.info('get_info: %s', msg)
        return msg
    except Exception as e:
        logger.exception(e)
    return 'None'
    # return node.get_node().api.get_info(is_json=False)

@app.post("/v1/chain/push_read_only_transaction", response_class=PlainTextResponse)
async def push_ro_transaction(args: PushReadOnlyTransactionArgs):
    global g_worker
    packed_tx = bytes.fromhex(args.packed_tx)

    with g_worker.rwlock.rlock():
        return node.get_node().chain.push_ro_transaction(packed_tx, return_json=False)

@app.post("/v1/chain/get_table_rows", response_class=PlainTextResponse)
async def get_table_rows(req: Request):
    global g_worker
    kwargs = await req.json()
    logger.info('get_table_rows: %s', kwargs)
    with g_worker.rwlock.rlock():
        ret = node.get_node().api.get_table_rows(**kwargs, return_json=False)
        logger.info('get_table_rows: %s', ret)
        return ret

class Worker(object):
    def __init__(self, messenger: Messenger, rwlock, exit_event, rpc_address: str):
        uds = None
        host = None
        port = None
        try:
            if rpc_address.startswith('/'):
                uds = rpc_address
                host = None
                port = None
            else:
                host, port = rpc_address.split(':')
                port = int(port)
        except:
            logger.error('invalid rpc_address: %s', rpc_address)
            return None

        app.get("/")(read_root)
        app.middleware("http")(rate_limit.rate_limit_middleware)

        self.config = uvicorn.Config(app, host=host, port=port, uds=uds)
        self.server = UvicornServer(self.config)

        self.messenger = messenger
        self.exit_event = exit_event
        self.rwlock = rwlock

        self.in_shutdown = False

    async def start(self):
        try:
            # if port is in use, uvicorn will raise OSError and all sys.exit(-1) which should be avoided
            # so make sure to check port is in use before start the server
            await self.server.serve()
        except asyncio.exceptions.CancelledError:
            logger.info('worker: asyncio.exceptions.CancelledError')
        except Exception as e:
            logger.exception(e)
        self.exit()

    def exit(self):
        eos.exit()
        self.server.exit()
        self.messenger.put(None)

    async def shutdown(self):
        if self.in_shutdown:
            logger.info("+++++++already in shutdown...")
            return
        self.exit()
        loop = asyncio.get_running_loop()
        tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
        for task in tasks:
            logger.info('wait for task: %s', task)
            # task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        # loop.stop()
        logger.info('shutdown done')

    def handle_signal(self, signum):
        logger.info("handle_signal: %s", signum)
        self.exit()

    async def main(self):
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGINT, self.handle_signal, signal.SIGINT)
        loop.add_signal_handler(signal.SIGTERM, self.handle_signal, signal.SIGTERM)

        asyncio.create_task(self.start())
        try:
            while not eos.should_exit():
                await asyncio.sleep(0.1)
        except asyncio.exceptions.CancelledError:
            logger.info('worker: asyncio.exceptions.CancelledError')

        self.exit_event.set()
        await self.shutdown()

    def exit_listener(self):
        self.exit_event.wait()
        self.exit()
        logger.info('exit_listener')

def run(rpc_address, rwlock: Lock, messenger: Messenger, exit_event: Event, data_dir: str, config_dir: str, state_size: int):
    global g_worker
    try:
        g_worker = Worker(messenger, rwlock, exit_event, rpc_address)
        _node = node.init_worker_node(data_dir, config_dir, state_size, rwlock)
        _node.chain.start_block()
    except DatabaseGuardException as e:
        logger.error('DatabaseGuardException: %s', e)
        messenger.put(None)
        return
    except Exception as e:
        logger.exception(e)
        messenger.put(None)
        return

    messenger.put('init done')
    threading.Thread(target=g_worker.exit_listener).start()


    logger.info('worker process starting...')
    if sys.version_info >= (3, 11):
        with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
            try:
                runner.run(g_worker.main())
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt")
    else:
        uvloop.install()
        try:
            asyncio.run(g_worker.main())
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")

