import sys
import json

from . import _eos
from typing import Union
from .types import Name

class NativeType:
    handshake_message = 0
    chain_size_message = 1
    go_away_message = 2
    time_message = 3
    notice_message = 4
    request_message = 5
    sync_request_message = 6
    signed_block_v0 = 7         # which = 7
    packed_transaction_v0 = 8   # which = 8
    signed_block = 9            # which = 9
    trx_message_v1 = 10         # which = 10
    genesis_state = 11
    abi_def = 12

def set_log_level(logger_name: str, level: int) -> None:
    _eos.set_log_level(logger_name, level)

def pack_native_object(_type: int, obj: Union[dict, str]) -> bytes:
    if isinstance(obj, dict):
        obj = json.dumps(obj)
    else:
        assert isinstance(obj, (str, bytes))
    return _eos.pack_native_object(_type, obj)

def unpack_native_object(_type: int, packed_obj: bytes) -> dict:
    return _eos.unpack_native_object(_type, packed_obj)

def pack_block(obj: Union[dict, str]) -> bytes:
    if isinstance(obj, dict):
        obj = json.dumps(obj)
    else:
        assert isinstance(obj, (str, bytes))
    return _eos.pack_native_object(NativeType.signed_block, obj)

def unpack_block(packed_obj: bytes) -> dict:
    return _eos.unpack_native_object(NativeType.signed_block, packed_obj)

def unpack_transaction(packed_obj: bytes) -> dict:
    return _eos.unpack_native_object(NativeType.packed_transaction_v0, packed_obj)

def pack_abi(abi: str) -> bytes:
    if not abi:
        return b''
    return pack_native_object(NativeType.abi_def, abi)

def s2n(s: str) -> int:
    '''
    Convert a EOSIO name to uint64_t
    '''
    return _eos.s2n(s)

def n2s(n: int) -> str:
    '''
    Convert int to a EOSIO name
    '''
    return _eos.n2s(n)

def s2b(s: str) -> bytes:
    n = s2n(s)
    return int.to_bytes(n, 8, 'little')

def b2s(s: bytes) -> str:
    s = int.from_bytes(s, 'little')
    return n2s(s)

def get_native_contract(contract) -> str:
    contract = _eos.s2n(contract)
    return _eos.get_native_contract(contract)

def enable_native_contracts(debug) -> None:
    _eos.enable_native_contracts(debug)

def is_native_contracts_enabled() -> bool:
    return _eos.is_native_contracts_enabled()

def enable_debug(debug) -> None:
    _eos.enable_debug(debug)

def is_debug_enabled() -> bool:
    return _eos.is_debug_enabled()

def get_last_error() -> str:
    return _eos.get_last_error()

def create_key(key_type: str = "K1") -> dict:
    ret = _eos.create_key(key_type)
    return json.loads(ret)

def check_ret(ret):
    if not ret:
        raise Exception(get_last_error())
    return ret

def get_public_key(priv_key: str) -> str:
    ret = _eos.get_public_key(priv_key)
    return check_ret(ret)

def sign_digest(priv_key: str, digest: str):
    ret = _eos.sign_digest(priv_key, digest)
    return check_ret(ret)

def init(argv=None) -> bool:
    if argv:
        return _eos.init(argv)
    return _eos.init(sys.argv)

def start() -> None:
    _eos.start()
