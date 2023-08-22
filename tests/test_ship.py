import asyncio
import json
import websockets
import pytest

from ipyeos import eos
from ipyeos.bases import log
from ipyeos.packer import Packer, Encoder, Decoder
from ipyeos.extensions.state_history import GetStatusRequestV0, BlockPosition, GetBlocksRequestV0, GetBlocksAckRequestV0
from ipyeos.extensions.state_history import StateRequest, GetStatusResultV0, GetBlocksResultV0
from ipyeos.bases.types import U32, Checksum256

logger = log.get_logger(__name__)

async def send(ws, method, params):
    msg = [method, params]
    await ws.send(json.dumps(msg))

# struct get_status_request_v0 {};

@pytest.mark.asyncio
async def test_ship():
    uri = "ws://127.0.0.1:8081"
    ws = await websockets.connect(uri)
    # while True:
    msg = await ws.recv()
    print(msg)

    req = GetStatusRequestV0()
    req = StateRequest(req)
    await ws.send(req.get_bytes())
    
    msg = await ws.recv()
    logger.info("++++++++msg: %s", msg)

    dec = Decoder(msg[1:])
    status = GetStatusResultV0.unpack(dec)
    logger.info("++++++++status: %s", status)

    req = GetBlocksRequestV0(status.last_irreversible.block_num, 0xffffffff, 1, [], False, True, True, True)
    req = StateRequest(req)
    await ws.send(req.get_bytes())

    # msg = await ws.recv()
    # logger.info('++++received:%s', msg)

    while True:
        req = GetBlocksAckRequestV0(1)
        req = StateRequest(req)
        await ws.send(req.get_bytes())
        msg = await ws.recv()
        dec = Decoder(msg)
        assert dec.unpack_u8() == 1, f'unknown type: {msg}'
        result = GetBlocksResultV0.unpack(dec)
        block = eos.unpack_block(result.block)
        logger.info('++++received: %s', result)
        logger.info('++++block: %s', block)
        # await asyncio.sleep(1.0)
