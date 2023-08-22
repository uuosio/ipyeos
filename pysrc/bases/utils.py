import socket
import struct
from typing import Union

from . import log
from .types import U32, F64, F128, Checksum256

logger = log.get_logger(__name__)

def to_bytes(value: Union[int, F64, F128], size: int = 8, signed=False) -> bytes:
    if isinstance(value, int):
        return value.to_bytes(size, byteorder='little', signed=signed)
    elif isinstance(value, float):
        assert size == 8
        return struct.pack('<d', value)
    elif isinstance(value, F128):
        # assert size == 16
        return value.get_bytes()
    raise Exception('Invalid type: ' + str(type(value)))

def i2b(value: int, size: int = 8) -> bytes:
    return value.to_bytes(size, byteorder='little', signed=True)

def u2b(value: int, size: int = 8) -> bytes:
    return value.to_bytes(size, byteorder='little', signed=False)

def f2b(value: float) -> bytes:
    return struct.pack('<d', value)

def get_block_num_from_block_id(block_id: str) -> U32:
    assert len(block_id) == 64
    assert isinstance(block_id, str)
    return int.from_bytes(bytes.fromhex(block_id[:8]), 'big')

#    inline block_id_type make_block_id( uint32_t block_num ) {
#       chain::block_id_type block_id;
#       block_id._hash[0] = fc::endian_reverse_u32(block_num);
#       return block_id;
#    }

def make_block_id(block_num: U32) -> Checksum256:
    return Checksum256(block_num.to_bytes(4, byteorder='big') + b'\x00' * 28)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_free_port():
    port = 7777
    if 'DEBUG_PORT' in os.environ:
        return int(os.environ['DEBUG_PORT'])

    for i in range(10):
        port = 7777 + i
        if not is_port_in_use(port):
            return port

    raise Exception('can not find a free port')

def is_unix_socket_available(socket_path):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    try:
        sock.connect(socket_path)
    except socket.error:
        return False
    finally:
        sock.close()

    return True

def is_socket_available(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
    except OSError:
        return True
    finally:
        sock.close()

    return False

def can_listen(rpc_address):
    try:
        if rpc_address.startswith('/') or rpc_address.startswith('./'):
            return not is_unix_socket_available(rpc_address)
        else:
            host, port = rpc_address.split(':')
            port = int(port)
            return not is_socket_available(host, port)
    except:
        logger.error('invalid rpc_address: %s', rpc_address)
        return False
