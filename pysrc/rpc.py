import asyncio
import json
import uvicorn

from aiocache import cached, Cache
from aiocache.serializers import StringSerializer
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel

from .uvicorn_server import UvicornServer
from . import log, net, node, node_config, rate_limit
from .chain_exceptions import BlockValidateException, InvalidSnapshotRequestException, SnapshotRequestNotFoundException, ChainException

logger = log.get_logger(__name__)

app = FastAPI()

class Item(BaseModel):
    code: str

class PushTransactionArgs(BaseModel):
    """
    A Pydantic model that represents the arguments for the `push_transaction` RPC method.

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
    speculate: bool = False

class GetBlockTraceArgs(BaseModel):
    """
    A Pydantic model that represents the arguments for the `get_block_trace` RPC method.
    """
    block_num: int

# start_block_num=num, end_block_num=num + 9, block_spacing=3, snapshot_description="1"
class SnapshotScheduleArgs(BaseModel):
    """
    A Pydantic model that represents the arguments for the `snapshot_schedule` RPC method.
    """
    start_block_num: int
    end_block_num: int
    block_spacing: int
    snapshot_description: str

class SnapshotUnscheduleArgs(BaseModel):
    """
    A Pydantic model that represents the arguments for the `snapshot_unschedule` RPC method.
    """
    schedule_request_id: int

async def read_root():
    """
    Returns a JSON object with a single key-value pair: "Hello" -> "World".
    """
    return {"Hello": "World"}

@app.get("/v1/chain/get_info", response_class=PlainTextResponse)
@cached(ttl=1, cache=Cache.MEMORY, key="get_info", serializer=StringSerializer())
async def get_info():
    rwlock = node.get_node().rwlock
    if rwlock:
        with rwlock.rlock():
            return node.get_node().api.get_info(is_json=False)
    else:
        return node.get_node().api.get_info(is_json=False)

@app.post("/v1/chain/get_table_rows", response_class=PlainTextResponse)
async def get_table_rows(req: Request):
    global g_worker
    params = await req.body()
    rwlock = node.get_node().rwlock
    if rwlock:
        with rwlock.rlock():
            ret = node.get_node().api.get_table_rows_ex(params, return_json=False)
            return ret
    else:
        ret = node.get_node().api.get_table_rows_ex(params, return_json=False)
        return ret

def generate_response(result):
    content = {"status": "ok", "result": result}
    return JSONResponse(content=content, status_code=200)

def generate_error_response(result):
    content = {"status": "error", "result": result}
    return JSONResponse(content=content, status_code=400)

@app.post("/v1/chain/push_transaction")
async def push_transaction(args: PushTransactionArgs):
    """
    Sends a packed transaction to the network.

    Args:
        args: An instance of the PushTransactionArgs model that contains the packed transaction data.

    Returns:
        The response from the network.
    """
    packed_tx = bytes.fromhex(args.packed_tx)

    conn = await node.get_network().get_connection()
    if not conn:
        return generate_error_response("no node connection")
    msg = net.PackedTransactionMessage(packed_tx)

    if not args.speculate:
        if await conn.send_message(msg):
            return generate_response('send transaction success')
        else:
            return generate_error_response('send transaction failed')

    ret = None
    success = False
    chain = node.get_node().chain
    try:
        rwlock = node.get_node().rwlock
        if rwlock:
            with rwlock.wlock():
                chain.start_block()
                success, ret = chain.push_transaction_ex(packed_tx, return_json=False)
                chain.abort_block()
        else:
            chain.start_block()
            success, ret = chain.push_transaction_ex(packed_tx, return_json=False)
            chain.abort_block()
    except Exception as e:
        return generate_error_response(str(e))

    if success:
        if await conn.send_message(msg):
            return generate_response(ret)
        return generate_error_response('send transaction failed')
    else:
        return generate_error_response(ret)

async def trace_api_get_block_trace(args: GetBlockTraceArgs):
    try:
        logger.error("++++++++args.block_num: %s", args.block_num)
        ret = node.get_node().get_trace().get_block_trace(args.block_num)
        if ret == 'null':
            return '{"code":404,"message":"Trace API: block trace missing","error":{"code":0,"name":"","what":"","details":[]}}'
        return ret
    except Exception as e:
        logger.exception(e)
        return f'{str(e)}'

async def snapshot_schedule(args: SnapshotScheduleArgs):
    try:
        ret = node.get_node().get_snapshot().schedule(args.start_block_num, args.end_block_num, args.block_spacing, args.snapshot_description)
        return f'{{"status": "ok", "result": {ret}}}'
    except InvalidSnapshotRequestException:
        return '{"status": "error", "result": "invalid snapshot request"}'

async def snapshot_unschedule(args: SnapshotUnscheduleArgs):
    try:
        ret = node.get_node().get_snapshot().unschedule(args.schedule_request_id)
        return f'{{"status": "ok", "result": {ret}}}'
    except SnapshotRequestNotFoundException:
        return '{"status": "error", "result": "invalid snapshot request"}'

async def snapshot_get_requests():
    ret = node.get_node().get_snapshot().get_requests()
    return f'{{"status": "ok", "result": {ret}}}'

def add_post_method(path, func):
    app.post(path, response_class=PlainTextResponse)(func)

def add_get_method(path, func):
    app.get(path, response_class=PlainTextResponse)(func)

def init(rpc_address: str):
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

    try:
        plugins = node_config.get_config()['plugins']

        if 'trace_api' in plugins:
            add_post_method("/v1/trace_api/get_block", trace_api_get_block_trace)
            logger.info('+++++add get_block_trace method')

        if 'snapshot' in plugins:
            logger.info('+++++add snapshot methods')
            add_post_method("/snapshot_schedule", snapshot_schedule)
            add_post_method("/snapshot_unschedule", snapshot_unschedule)
            add_get_method("/snapshot_get_requests", snapshot_get_requests)
    except Exception as e:
        logger.exception(e)
        logger.info('+++++no plugins in config file')
    
    config = uvicorn.Config(app, host=host, port=port, uds=uds)
    server = UvicornServer(config)
    return server

async def start(server):
    try:
        await server.serve()
    except asyncio.exceptions.CancelledError:
        logger.info('asyncio.exceptions.CancelledError')

if __name__ == '__main__':
    asyncio.run(run(8088))
