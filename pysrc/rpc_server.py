import json
import asyncio as aio
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from waitress import serve

from .interfaces.ttypes import Action, ActionArguments
from . import eos

from typing import NewType, Dict, Optional
i32 = NewType('i32', int)
i64 = NewType('i64', int)
u64 = NewType('u64', int)

class BaseChainTester:
    def produce_block(self, id):
        pass

    def push_action(self, id: int, account: str, action: str, arguments: str, permissions: str):
        pass

    def push_actions(self, id, actions):
        pass

    def get_table_rows(self, id, _json: bool, code: str, scope: str, table: str, lower_bound: str, upper_bound: str, limit: i64, key_type: str, index_position: str, reverse: bool, show_payer: bool):
        pass

    def enable_debug_contract(self, id, contract, enable):
        pass

    def is_debug_contract_enabled(self, id, contract):
        pass

    def pack_abi(self, abi):
        pass

    def pack_action_args(self, id, contract, action, action_args):
        pass

    def unpack_action_args(self, id, contract, action, raw_args):
        pass

    def new_chain(self):
        pass

    def free_chain(self, id):
        pass

    def get_info(self, id: i32):
        pass

    def get_account(self, id: i32, account: str):
        pass

    def import_key(self, id: i32, pub_key: str, priv_key: str):
        pass

    def get_required_keys(self, id: i32, transaction: str, available_keys: list[str]):
        pass

class ChainTesterProxy(object):
    def __init__(self, handler: BaseChainTester):
        self.handler = handler

    def new_chain(self):
        id = self.handler.new_chain()
        return {"id": id}

    def free_chain(self, id):
        self.handler.free_chain(id)
        return {}

    def create_key(self, key_type):
        return eos.create_key(key_type)

    def get_public_key(self, priv_key):
        ret = eos.get_public_key(priv_key)
        return {'data': ret}

    def get_info(self, id: i32):
        ret = self.handler.get_info(id)
        return ret

    def get_account(self, id: i32, account: str):
        return self.handler.get_account(id, account)

    def create_account(self, id: int, creator: str, account: str, owner_key: str, active_key: str, ram_bytes: int=0, stake_net: int=0, stake_cpu: int=0):
        return self.handler.create_account(id, creator, account, owner_key, active_key, ram_bytes, stake_net, stake_cpu)

    def produce_block(self, id, next_block_skip_seconds: int=0):
        self.handler.produce_block(id, next_block_skip_seconds)
        return {}

    def push_action(self, id: int, account: str, action: str, arguments: str, permissions: str):
        _arguments = ActionArguments(json_args=arguments)
        return self.handler.push_action(id, account, action, _arguments, permissions)

    def push_actions(self, id, actions):
        actions = json.loads(actions)
        _actions = []
        for a in actions:
            _a = Action(**a)
            _a.arguments = ActionArguments(json_args=json.dumps(_a.arguments))
            _a.permissions = json.dumps(_a.permissions)
            _actions.append(_a)
        return self.handler.push_actions(id, _actions)

    def deploy_contract(self, id, account: str, wasm: str, abi: str):
        return self.handler.deploy_contract(id, account, wasm, abi)

    def get_table_rows(self, id, _json: bool, code: str, scope: str, table: str, lower_bound: str, upper_bound: str, limit: i64, key_type: str, index_position: str, reverse: bool, show_payer: bool):
        return self.handler.get_table_rows(id, _json, code, scope, table, lower_bound, upper_bound, limit, key_type, index_position, reverse, show_payer)

    def enable_debug_contract(self, id, contract, enable):
        self.handler.enable_debug_contract(id, contract, enable)
        return {"data": "ok"}

    def is_debug_contract_enabled(self, id, contract):
        ret = self.handler.is_debug_contract_enabled(id, contract)
        return {"data": ret}

    def pack_abi(self, abi):
        ret = self.pack_abi(abi)
        return {"data": ret.hex()}

    def pack_action_args(self, id, contract, action, action_args):
        try:
            ret = self.handler.pack_action_args(id, contract, action, action_args)
            return {'data': ret.hex()}
        except Exception as e:
            return {'error': e.args[0]}

    def unpack_action_args(self, id, contract, action, raw_args):
        ret = self.handler.unpack_action_args(id, contract, action, raw_args)
        return {"data": ret}

    def import_key(self, id: i32, pub_key: str, priv_key: str):
        ret = self.handler.import_key(id, pub_key, priv_key)
        return {"data": "ok"}

    def get_required_keys(self, id: i32, transaction: str, available_keys: list[str]):
        ret = self.handler.get_required_keys(id, transaction, available_keys)
        return {"data": ret}

proxy = None
app = Flask(__name__)

@app.route('/api/<method>', methods=['GET', 'POST'])
def call_method(method):
    global proxy
    kwargs = request.json
    # print(kwargs)
    ret = getattr(proxy, method)(**kwargs)
    if isinstance(ret, dict):
        ret = json.dumps(ret)
    return ret

def start(rpc_server_addr, rpc_server_port, handler: BaseChainTester):
    global proxy
    proxy = ChainTesterProxy(handler)
    serve(app, listen=f'{rpc_server_addr}:{rpc_server_port}')
