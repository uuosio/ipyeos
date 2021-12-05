import sys
import json

from . import _uuos
from typing import Union
from ipyeos.uuostyping import Name

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
    _uuos.set_log_level(logger_name, level)

def set_block_interval_ms(ms: int) -> None:
    _uuos.set_block_interval_ms(ms)

def pack_native_object(_type: int, obj: Union[dict, str]) -> bytes:
    if isinstance(obj, dict):
        obj = json.dumps(obj)
    else:
        assert isinstance(obj, (str, bytes))
    return _uuos.pack_native_object(_type, obj)

def unpack_native_object(_type: int, packed_obj: bytes) -> dict:
    return _uuos.unpack_native_object(_type, packed_obj)

def pack_block(obj: Union[dict, str]) -> bytes:
    if isinstance(obj, dict):
        obj = json.dumps(obj)
    else:
        assert isinstance(obj, (str, bytes))
    return _uuos.pack_native_object(NativeType.signed_block, obj)

def unpack_block(packed_obj: bytes) -> dict:
    return _uuos.unpack_native_object(NativeType.signed_block, packed_obj)

def unpack_transaction(packed_obj: bytes) -> dict:
    return _uuos.unpack_native_object(NativeType.packed_transaction_v0, packed_obj)

def pack_abi(abi: str) -> bytes:
    return pack_native_object(NativeType.abi_def, abi)

def s2n(s: str) -> int:
    '''
    Convert a EOSIO name to uint64_t
    '''
    return _uuos.s2n(s)

def n2s(n: int) -> str:
    '''
    Convert int to a EOSIO name
    '''
    return _uuos.n2s(n)

def s2b(s: str) -> bytes:
    n = s2n(s)
    return int.to_bytes(n, 8, 'little')

def b2s(s: bytes) -> str:
    s = int.from_bytes(s, 'little')
    return n2s(s)

def set_native_contract(contract: Name, native_contract_lib) -> bool:
    return _uuos.set_native_contract(contract, native_contract_lib)

def get_native_contract(contract) -> str:
    return _uuos.get_native_contract(contract)

def enable_native_contracts(debug) -> None:
    _uuos.enable_native_contracts(debug)

def is_native_contracts_enabled() -> bool:
    return _uuos.is_native_contracts_enabled()

def init(argv=None) -> bool:
    if argv:
        return _uuos.init(argv)
    return _uuos.init(sys.argv)

def exec() -> None:
    _uuos.exec()
