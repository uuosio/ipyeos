import struct
from typing import Union

from .types import F64, F128

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
