import os
import sys
import json
import struct
import pytest

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
        print(tp, id, raw_data)
        if tp == 1:
            print(eos.b2s(raw_data[:8]))
        return 1
    object_types = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31, 32, 33, 34, 38, 39, 40, 41]

    for tp in object_types:
        if tp in [15, 40]: #block_summary_object, code_object
            continue
        chain.db.walk(tp, 0, on_data)

@chain_test(True)
def test_walk_range(chain: ChainTester):
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

@chain_test(True)
def test_find(chain: ChainTester):
    def on_data(tp, id, raw_data):
        print(tp, id, raw_data)
        if tp == 1:
            print(eos.b2s(raw_data[:8]))
        return 1
    object_types = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31, 32, 33, 34, 38, 39, 40, 41]

    for tp in object_types:
        if tp in [15, 40]: #block_summary_object, code_object
            continue
        print(tp)
        ret, raw_data = chain.db.find(tp, 0, int.to_bytes(0, 8, 'little'), max_buffer_size=1024)
        print(ret, raw_data)
