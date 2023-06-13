import os
import sys
import json
import struct
import pytest
import time

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, '..'))

from ipyeos import eos, log
from ipyeos import chaintester
from ipyeos.chaintester import ChainTester

chaintester.chain_config['contracts_console'] = True

logger = log.get_logger(__name__)

def update_auth(chain, account):
    a = {
        "account": account,
        "permission": "active",
        "parent": "owner",
        "auth": {
            "threshold": 1,
            "keys": [
                {
                    "key": 'EOS6AjF6hvF7GSuSd4sCgfPKq5uWaXvGM2aQtEUCwmEHygQaqxBSV',
                    "weight": 1
                }
            ],
            "accounts": [{"permission":{"actor":account,"permission": 'eosio.code'}, "weight":1}],
            "waits": []
        }
    }
    chain.push_action('eosio', 'updateauth', a, {account:'active'})

def init_chain(initialize=True):
    chain = chaintester.ChainTester(initialize)
    # update_auth(chain, 'hello')
    return chain

def chain_test(initialize=True):
    def init_call(fn):
        def call(*args, **vargs):
            chain = init_chain(initialize)
            ret = fn(chain, *args, **vargs)
            chain.free()
            return ret
        return call
    return init_call

class NewChain():
    def __init__(self):
        self.chain = None

    def __enter__(self):
        self.chain = init_chain()
        return self.chain

    def __exit__(self, type, value, traceback):
        self.chain.free()

def unpack_length(val: bytes):
    assert len(val) > 0, "raw VarUint32 value cannot be empty"
    v = 0
    by = 0
    n = 0
    for b in val:
        v |= (b & 0x7f) << by
        by += 7
        n += 1
        if b & 0x80 == 0:
            break
    return v, n

test_dir = os.path.dirname(__file__)
def deploy_contract(package_name):
    with open(f'{test_dir}/{package_name}.wasm', 'rb') as f:
        code = f.read()
    with open(f'{test_dir}/{package_name}.abi', 'rb') as f:
        abi = f.read()
    chain.deploy_contract('hello', code, abi)

@chain_test(True)
def test_walk(chain: ChainTester):
    def on_data(tp, id, raw_data):
        print(tp, id, len(raw_data))
        if tp == 1:
            print(eos.b2s(raw_data[:8]))
        return 1
    object_types = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31, 32, 33, 34, 38, 39, 40, 41]
    for tp in object_types:
        if tp in [15, ]: #block_summary_object, code_object
            continue
        chain.db.walk(tp, 0, on_data)

@chain_test(True)
def test_2walk_range(chain: ChainTester):
    def on_data(tp, id, raw_data):
        print(tp, id, raw_data)
        if tp == 1:
            print(eos.b2s(raw_data[:8]))
        return 1
    object_types = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31, 32, 33, 34, 38, 39, 40, 41]

    for tp in object_types:
        if tp in [15, 40]: #block_summary_object, code_object
            continue
        chain.db.walk_range(tp, 0, on_data, int.to_bytes(0, 8, 'little'), int.to_bytes(10, 8, 'little'))

def parse_code(raw_data: bytes):
    print('+++++++raw_data:', len(raw_data))
    pos = 0
    code_hash = raw_data[:32]
    print('+++code hash:', code_hash)
    pos += 32
    length, length_size = unpack_length(raw_data[pos:])
    pos += length_size
    code = raw_data[pos:pos + length]
    pos += length
    code_ref_count = int.from_bytes(raw_data[pos:pos+8], 'little')
    pos += 8
    first_block_used = int.from_bytes(raw_data[pos:pos+4], 'little')
    pos += 4
    vm_type = raw_data[pos]
    pos += 1
    vm_version = raw_data[pos]
    print(code_ref_count, first_block_used, vm_type, vm_version)
    print('len(code):', len(code))
    # with open('out.wasm', 'wb') as f:
    #     f.write(code)
    return code_hash

@chain_test(True)
def test_find(chain: ChainTester):
    object_types = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31, 32, 33, 34, 38, 39, 40, 41]

    for tp in object_types:
        if tp in [15, ]: #block_summary_object, code_object
            continue
        raw_data = chain.db.find(tp, 0, int.to_bytes(0, 8, 'little'))
        if raw_data:
            print(tp, len(raw_data))

    if 0:
        key = int.to_bytes(1, 8, 'little')
        print('++++key:', key)
        raw_data = chain.db.find(40, 0, key)
        code_hash = parse_code(raw_data)
        # digest_type  code_hash; //< code_hash should not be changed within a chainbase modifier lambda
        # shared_blob  code;
        # uint64_t     code_ref_count;
        # uint32_t     first_block_used;
        # uint8_t      vm_type = 0; //< vm_type should not be changed within a chainbase modifier lambda
        # uint8_t      vm_version = 0; //< vm_version should not be changed within a chainbase modifier lambda

        #find with by_code_hash
        raw_key = code_hash + int.to_bytes(0, 1, 'little') + int.to_bytes(0, 1, 'little')
        raw_data = chain.db.find(40, 1, raw_key)
        parse_code(raw_data)


@chain_test(True)
def test_lower_bound(chain: ChainTester):
    object_types = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31, 32, 33, 34, 38, 39, 40, 41]
    start = time.time()
    for tp in object_types:
        if tp in [15, ]: #block_summary_object, code_object
            continue
        raw_data = chain.db.lower_bound(tp, 0, int.to_bytes(0, 8, 'little'))
        if raw_data:
            print(tp, len(raw_data))

    raw_data = chain.db.lower_bound(40, 0, int.to_bytes(1, 8, 'little'))
    print(40, len(raw_data))

    raw_data = chain.db.upper_bound(40, 0, int.to_bytes(1, 8, 'little'))
    print(40, len(raw_data))

    raw_data = chain.db.lower_bound(40, 0, int.to_bytes(0, 8, 'little'))
    print(40, len(raw_data))

    raw_data = chain.db.upper_bound(40, 0, int.to_bytes(0, 8, 'little'))
    print(40, len(raw_data))
    
    print(time.time() - start)
