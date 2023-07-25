import struct
from typing import Any, List, Type, Union

from . import eos
from .types import (I16, I64, U8, U16, U32, U64, U128, U256, Checksum256, Name,
                    PublicKey)


def pack_length(val: int):
    result = bytearray()
    while True:
        b = val & 0x7f
        val >>= 7
        if val > 0:
            b |= 0x80
        result.append(b)
        if val <= 0:
            break
    return bytes(result)

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

class Packer(object):
    def pack(self, enc):
        assert False, "Not implemented"

    def get_bytes(self):
        enc = Encoder()
        self.pack(enc)
        return enc.get_bytes()

    @classmethod
    def unpack_bytes(cls, raw: bytes):
        dec = Decoder(raw)
        return cls.unpack(dec)

    @classmethod
    def unpack(cls, dec):
        assert False, "Not implemented"

class Encoder(object):

    def __init__(self):
        self.data = []
        self.pos = 0

    def write_bytes(self, raw: bytes):
        self.data.append(raw)
        self.pos += len(raw)

    def pack(self, obj: Any) -> int:
        return obj.pack(self)

    def pack_bool(self, b: bool) -> int:
        if b:
            self.write_bytes(b'\x01')
        else:
            self.write_bytes(b'\x00')

    def pack_u8(self, n: U8) -> int:
        raw = int.to_bytes(n, 1, 'little')
        self.write_bytes(raw)
        return 1

    def pack_i16(self, n: I16):
        raw = int.to_bytes(n, 2, 'little', signed=True)
        self.write_bytes(raw)
        return 2

    def pack_u16(self, n: U16) -> int:
        raw = int.to_bytes(n, 2, 'little')
        self.write_bytes(raw)
        return 2

    def pack_u32(self, n: U32) -> int:
        raw = int.to_bytes(n, 4, 'little')
        self.write_bytes(raw)
        return 4

    def pack_u64(self, n: U64) -> int:
        raw = int.to_bytes(n, 8, 'little')
        self.write_bytes(raw)
        return 8

    def pack_i64(self, n: I64):
        raw = int.to_bytes(n, 8, 'little', signed=True)
        self.write_bytes(raw)
        return 8

    def pack_u128(self, n: U128):
        raw = int.to_bytes(n, 16, 'little')
        self.write_bytes(raw)
        return 16
    
    def pack_u256(self, n: U256):
        raw = int.to_bytes(n, 32, 'little')
        self.write_bytes(raw)
        return 32
    
    def pack_double(self, n: float):
        raw = struct.pack('d', n)
        self.write_bytes(raw)
        return 8

    def pack_length(self, val: U32):
        result = bytearray()
        while True:
            b = val & 0x7f
            val >>= 7
            if val > 0:
                b |= 0x80
            result.append(b)
            if val <= 0:
                break
        bs = bytes(result)
        self.write_bytes(bs)
        return len(bs)

    def pack_name(self, s: Union[str, Name]):
        if isinstance(s, str):
            raw = eos.s2b(s)
        else:
            raw = s.to_bytes()
        self.write_bytes(raw)
        return 8

    def pack_checksum256(self, h: Union[bytes, Checksum256]):
        if isinstance(h, bytes):
            assert len(h) == 32, "invalid checksum256"
            self.write_bytes(h)
            return 32            
        assert isinstance(h, Checksum256)
        h.pack(self)
        return 32

    def pack_bytes(self, data: bytes):
        self.pack_length(len(data))
        self.write_bytes(data)
        return len(data)

    def pack_string(self, s: str):
        raw = s.encode()
        self.pack_length(len(raw))
        self.write_bytes(raw)
        return len(raw)

    def pack_list(self, l: List[Type]):
        pos = self.get_pos()
        self.pack_length(len(l))
        for item in l:
            if isinstance(item, str):
                self.pack_string(item)
            else:
                self.pack(item)
        return self.get_pos() - pos

    def pack_optional(self, value: Any, tp: Type=None):
        if value is None:
            self.pack_u8(0)
            return 1
        self.pack_u8(1)

        if isinstance(value, Packer):
            return self.pack(value) + 1

        if tp is U32:
            return self.pack_u32(value) + 1
        elif tp is U64:
            return self.pack_u64(value) + 1
        elif tp is U128:
            return self.pack_u128(value) + 1
        elif tp is U256:
            return self.pack_u256(value) + 1
        elif tp is Name:
            return self.pack_name(value) + 1
        elif tp is Checksum256:
            return self.pack_checksum256(value) + 1
        elif tp is str:
            return self.pack_string(value) + 1
        return self.pack(value) + 1

    def get_pos(self):
        return self.pos

    def get_bytes(self):
        return b''.join(self.data)

class Decoder(object):
    def __init__(self, raw_data: bytes):
        self.raw_data = raw_data
        self._pos = 0

    def read_bytes(self, size):
        assert len(self.raw_data) >= self._pos + size
        ret = self.raw_data[self._pos:self._pos+size]
        self._pos += size
        return ret

    def unpack(self, unpacker):
        return unpacker.unpack(self)

    def unpack_name(self):
        name = self.read_bytes(8)
        return eos.b2s(name)

    def unpack_bool(self):
        ret = self.read_bytes(1)[0]
        assert ret == 0 or ret == 1
        return ret != 0

    def unpack_u8(self):
        ret = self.read_bytes(1)[0]
        return ret

    def unpack_i16(self):
        ret = int.from_bytes(self.read_bytes(2), 'little', signed=True)
        return ret

    def unpack_u16(self):
        ret = int.from_bytes(self.read_bytes(2), 'little')
        return ret

    def unpack_u32(self):
        ret = int.from_bytes(self.read_bytes(4), 'little')
        return ret

    def unpack_u64(self):
        ret = int.from_bytes(self.read_bytes(8), 'little')
        return ret

    def unpack_i64(self):
        ret = int.from_bytes(self.read_bytes(8), 'little', signed=True)
        return ret
    
    def unpack_u128(self):
        ret = int.from_bytes(self.read_bytes(16), 'little')
        return ret

    def unpack_u256(self):
        ret = int.from_bytes(self.read_bytes(32), 'little')
        return ret
    
    def unpack_double(self):
        ret = struct.unpack('d', self.read_bytes(8))[0]
        return ret

    def unpack_checksum256(self):
        ret = self.read_bytes(32)
        return Checksum256(ret)

    def unpack_length(self):
        v = 0
        by = 0
        while True:
            b = self.unpack_u8()
            v |= (b & 0x7f) << by
            by += 7
            if b & 0x80 == 0:
                break
        return v

    def unpack_bytes(self):
        length = self.unpack_length()
        data = self.read_bytes(length)
        return data
    
    def unpack_string(self):
        length = self.unpack_length()
        data = self.read_bytes(length)
        return data.decode()
    
    def unpack_list(self, tp: Type):
        length = self.unpack_length()
        ret = []
        for _ in range(length):
            if tp is str:
                ret.append(self.unpack_string())
            else:
                ret.append(tp.unpack(self))
        return ret

    def unpack_optional(self, tp: Type):
        flag = self.unpack_u8()
        if flag == 0:
            return None
        if tp is U32:
            return self.unpack_u32()
        elif tp is U64:
            return self.unpack_u64()
        elif tp == bytes:
            return self.unpack_bytes()
        return tp.unpack(self)

    def unpack_time_point(self):
        return self.unpack_i64()

    def unpack_public_key(self):
        ret = PublicKey.unpack(self)
        return ret

    def get_bytes(self, size):
        ret = self.read_bytes(size)
        return ret
    
    @property
    def pos(self):
        return self._pos

    def reset_pos(self):
        self._pos = 0

    def get_pos(self):
        return self._pos

