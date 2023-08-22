import asyncio
import os
import hashlib
import logging
import shutil
import platform

import json
import websockets
import pytest

from ipyeos.tester import chaintester
from ipyeos.tester.chaintester import ChainTester

from ipyeos.extensions.state_history import StateHistory
from ipyeos.extensions.state_history import GetStatusRequestV0, BlockPosition, GetBlocksRequestV0, GetBlocksAckRequestV0
from ipyeos.extensions.state_history import StateRequest, GetStatusResultV0, GetBlocksResultV0
from ipyeos.core.chain_exceptions import SnapshotRequestNotFoundException, InvalidSnapshotRequestException

from ipyeos import eos
from ipyeos.bases import log
from ipyeos.bases.packer import Packer, Encoder, Decoder
from ipyeos.bases.types import U32, Checksum256


chaintester.chain_config['contracts_console'] = True
dir_name = os.path.dirname(__file__)

logger = logging.getLogger(__name__)

async def send(ws, method, params):
    msg = [method, params]
    await ws.send(json.dumps(msg))

test_dir = os.path.dirname(__file__)
def deploy_contract(tester, package_name):
    with open(f'{test_dir}/{package_name}.wasm', 'rb') as f:
        code = f.read()
    with open(f'{test_dir}/{package_name}.abi', 'rb') as f:
        abi = f.read()
    tester.deploy_contract('hello', code, abi)

from ipyeos.bases.packer import Packer, Encoder, Decoder
from ipyeos.core.database import AccountObject, AccountMetadataObject, CodeObject

def parse_deltas(deltas):
    dec = Decoder(deltas)
    num_tables = dec.unpack_length()
    logger.info(num_tables)
    for i in range(num_tables):
        variant_index = dec.unpack_u8()
        table_name = dec.unpack_string()
        num_entries = dec.unpack_length()
        logger.info(f'{variant_index} {table_name} {num_entries}')
        for _ in range(num_entries):
            is_removed_value = dec.unpack_bool()
            length = dec.unpack_length()
            variant_index = dec.unpack_u8()
            assert variant_index == 0
            length -= 1
            # raw_obj = dec.read_bytes(length)
            if table_name == 'account':
                raw_obj = dec.read_bytes(length)
                # logger.info(raw_obj)

                # pos = dec.get_pos()
                # account = AccountObject.unpack(dec)
                # length2 = dec.get_pos() - pos
                # assert length == length2
                # logger.info("%s %s", length, length2)
                # logger.info(f'{is_removed_value} {variant_index} {account}')
            elif table_name == 'account_metadata':
                raw_obj = dec.read_bytes(length)
                # logger.info(raw_obj)
                # obj = AccountMetadataObject.unpack(dec)
                # logger.info(f'{is_removed_value} {variant_index} {obj}')
            elif table_name == 'code':
                # raw_obj = dec.read_bytes(length-1)
                # logger.info(raw_obj)
# struct code_v0 {
#     uint8_t             vm_type    = {};
#     uint8_t             vm_version = {};
#     eosio::checksum256  code_hash  = {};
#     eosio::input_stream code       = {};
# };
                vm_type = dec.unpack_u8()
                vm_version = dec.unpack_u8()
                code_hash = dec.read_bytes(32)
                code = dec.read_bytes(length-34)
                # logger.info(f'{is_removed_value} {variant_index} {vm_type} {vm_version} {code_hash} {code}')
                # code = CodeObject.unpack(dec)
                # logger.info(f'{is_removed_value} {variant_index} {code}')
            elif table_name == 'contract_row':
                raw_obj = dec.read_bytes(length)
                # logger.info(raw_obj)
            elif table_name == 'resource_usage':
                raw_obj = dec.read_bytes(length)
                # logger.info(raw_obj)
            else:
                raw_obj = dec.read_bytes(length)
                # logger.info(raw_obj)

@pytest.mark.asyncio
async def test_state_history():
    # t = ChainTester(True, data_dir=os.path.join(dir_name, "dd"), config_dir=os.path.join(dir_name, "cd"))
    t = ChainTester(True)

    s = StateHistory()
    s.initialize(t.chain, t.data_dir, trace_history=True, chain_state_history=True, state_history_log_retain_blocks=1000)
    s.startup()
    t.produce_block()
    start_block_num = t.chain.head_block_num()

    deploy_contract(t, 'test')
    t.produce_block()

    # uint64_t    secondary1,
    # uint128_t   secondary2,
    # checksum256 secondary3,
    # double      secondary4,
    # long double secondary5
    args = {
        'key': 0,
        'secondary1': 1,
        'secondary2': 2,
        'secondary3': (b'\x03' + b'\x00' * 31).hex(),
        'secondary4': "4.0",
        'secondary5': "0x" + '05'*16
    }
    r = t.push_action('hello', 'teststore', args, {'hello': 'active'})
    r = t.push_action('hello', 'sayhello', b'', {'hello': 'active'})
    t.produce_block()
    rows = t.get_table_rows(True, 'hello', '', 'mytable', '', '', 10)
    logger.info(rows)
    logger.info('+++++block num after teststore: %s', t.chain.head_block_num())

    uri = "ws://127.0.0.1:8080"
    ws = await websockets.connect(uri)
    # while True:
    msg = await ws.recv()
    # logger.info(msg)

    req = GetStatusRequestV0()
    req = StateRequest(req)
    await ws.send(req.get_bytes())
    
    msg = await ws.recv()
    logger.info("++++++++msg: %s", msg)

    dec = Decoder(msg[1:])
    status = GetStatusResultV0.unpack(dec)
    logger.info("++++++++status: %s", status)

    req = GetBlocksRequestV0(start_block_num, 0xffffffff, 1, [], False, True, True, True)
    req = StateRequest(req)
    await ws.send(req.get_bytes())

    for i in range(2):
        logger.info(i)
        req = GetBlocksAckRequestV0(1)
        req = StateRequest(req)
        await ws.send(req.get_bytes())
        msg = await ws.recv()
        dec = Decoder(msg)
        assert dec.unpack_u8() == 1, f'unknown type: {msg}'
        result = GetBlocksResultV0.unpack(dec)
        block = eos.unpack_block(result.block)
        logger.info('++++received: %s', result.this_block.block_num)
        # logger.info('++++received: %s', result.traces)

        ret = eos._eos.unpack_native_object2(0, result.traces)
        # logger.info(ret)

        # logger.info('++++block: %s', block)
        # logger.info('++++received: %s', result.deltas)
        parse_deltas(result.deltas)

    await ws.close()

