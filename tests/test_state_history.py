import asyncio
import os
import hashlib
import logging
import shutil
import platform

import json
import websockets
import pytest

from ipyeos import chaintester
from ipyeos.chaintester import ChainTester

from ipyeos.state_history import StateHistory
from ipyeos.state_history import GetStatusRequestV0, BlockPosition, GetBlocksRequestV0, GetBlocksAckRequestV0
from ipyeos.state_history import StateRequest, GetStatusResultV0, GetBlocksResultV0
from ipyeos.chain_exceptions import SnapshotRequestNotFoundException, InvalidSnapshotRequestException

from ipyeos import eos, log
from ipyeos.packer import Packer, Encoder, Decoder
from ipyeos.types import U32, Checksum256


chaintester.chain_config['contracts_console'] = True
dir_name = os.path.dirname(__file__)

logger = logging.getLogger(__name__)

async def send(ws, method, params):
    msg = [method, params]
    await ws.send(json.dumps(msg))

@pytest.mark.asyncio
async def test_state_history():
    # t = ChainTester(True, data_dir=os.path.join(dir_name, "dd"), config_dir=os.path.join(dir_name, "cd"), log_level=0)
    t = ChainTester(True, log_level=0)

    s = StateHistory()
    s.initialize(t.chain, t.data_dir)
    s.startup()

    for i in range(10):
        t.produce_block()

    uri = "ws://127.0.0.1:8080"
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

    req = GetBlocksRequestV0(1, 0xffffffff, 1, [], False, True, True, True)
    req = StateRequest(req)
    await ws.send(req.get_bytes())

    for i in range(10):
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

    await ws.close()
