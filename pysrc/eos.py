import json
import sys
from typing import Union
from enum import Enum

from . import _eos


class NativeType:
    handshake_message = 0
    chain_size_message = 1
    go_away_message = 2
    time_message = 3
    notice_message = 4
    request_message = 5
    sync_request_message = 6
    signed_block = 7         # which = 7
    packed_transaction = 8   # which = 8
    genesis_state = 9
    abi_def = 10
    transaction_type = 11
    global_property_type = 12

class LogLevel(Enum):
    ALL = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    OFF = 5

# "net_plugin"
# "http_plugin"
# "producer_plugin"
# "trace_api"
# "state_history"

def initialize_logging(logging_config_file: str="logging.json") -> None:
    _eos.initialize_logging(logging_config_file)

def set_log_level(logger_name: str, level: Union[int, LogLevel]) -> None:
    if isinstance(level, LogLevel):
        level = level.value
    _eos.set_log_level(logger_name, level)

def get_log_level(logger_name: str = "default") -> int:
    value = _eos.get_log_level(logger_name)
    return LogLevel(value)

def set_all_level(logger_name: str = 'default') -> None:
    _eos.set_log_level(logger_name, LogLevel.ALL.value)

def set_debug_level(logger_name: str = 'default') -> None:
    _eos.set_log_level(logger_name, LogLevel.DEBUG.value)

def set_info_level(logger_name: str = 'default') -> None:
    _eos.set_log_level(logger_name, LogLevel.INFO.value)

def set_warn_level(logger_name: str = 'default') -> None:
    _eos.set_log_level(logger_name, LogLevel.WARN.value)

def set_error_level(logger_name: str = 'default') -> None:
    _eos.set_log_level(logger_name, LogLevel.ERROR.value)

def set_off_level(logger_name: str = 'default') -> None:
    _eos.set_log_level(logger_name, LogLevel.OFF.value)

def pack_native_object(_type: int, obj: Union[dict, str]) -> bytes:
    if isinstance(obj, dict):
        obj = json.dumps(obj)
    else:
        assert isinstance(obj, (str, bytes))
    return _eos.pack_native_object(_type, obj)

def unpack_native_object(_type: int, packed_obj: bytes) -> dict:
    ret = _eos.unpack_native_object(_type, packed_obj)
    if not ret:
        raise Exception(_eos.get_last_error_and_clear())
    return ret

def pack_block(obj: Union[dict, str]) -> bytes:
    if isinstance(obj, dict):
        obj = json.dumps(obj)
    else:
        assert isinstance(obj, (str, bytes))
    return _eos.pack_native_object(NativeType.signed_block, obj)

def unpack_block(packed_obj: bytes) -> dict:
    return _eos.unpack_native_object(NativeType.signed_block, packed_obj)

def unpack_transaction(packed_obj: bytes) -> dict:
    return _eos.unpack_native_object(NativeType.packed_transaction, packed_obj)

def pack_abi(abi: str) -> bytes:
    if not abi:
        return b''
    return pack_native_object(NativeType.abi_def, abi)

def s2n(s: str) -> int:
    '''
    Convert a EOSIO name to uint64_t
    '''
    ret = _eos.s2n(s)
    if not ret == 0:
        return ret
    err = _eos.get_last_error_and_clear()
    if err:
        _eos.set_last_error("")
        raise Exception(err)
    return ret

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

def sym2n(s: str) -> int:
    """convert symbol string to int

    Args:
        s (str): symbol name

    Raises:
        Exception: invalid symbol

    Returns:
        _type_: int
    """
    for c in s:
        if not c.isupper():
            raise Exception('invalid symbol')
    ss = [c for c in s]
    ss.reverse()
    return int.from_bytes(''.join(ss).encode(), 'big')

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
    return _eos.get_last_error_and_clear()

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

def extract_chain_id_from_snapshot(snapshot: str) -> str:
    return _eos.extract_chain_id_from_snapshot(snapshot)

def sign_digest(digest: str, priv_key: str):
    ret = _eos.sign_digest(digest, priv_key)
    return check_ret(ret)

def init(argv=None) -> int:
    if argv:
        return _eos.init(argv)
    return _eos.init(sys.argv[1:])

def run() -> int:
    return _eos.run()

def run_once() -> int:
    return _eos.run_once()

def post(fn, *args, **kwargs):
    return _eos.post(fn, *args, **kwargs)

def quit() -> None:
    _eos.quit()

def base58_to_bytes(s: str):
    return _eos.base58_to_bytes(s)

def bytes_to_base58(data: bytes) -> str:
    return _eos.bytes_to_base58(data)
