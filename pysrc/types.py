import base58
import hashlib
from typing import NewType
# from . import eos

U8 = NewType('U8', int)
U16 = NewType('U16', int)
U32 = NewType('U32', int)
U64 = NewType('U64', int)
I64 = NewType('I64', int)
F64 = NewType('F64', float)
U128 = NewType('U128', int)
U256 = NewType('U256', int)
Name = NewType('Name', str)
TimePointSec = NewType('U32', int)

# class Name(object):
#     def __init__(self, s: str, raw = None):
#         self.s = s
#         if not raw:
#             self.raw = eos.s2b(s)
#         else:
#             self.raw = raw

#     def n2b(self):
#         return self.raw

#     def __repr__(self):
#         return self.s
    
#     def __eq__(self, other):
#         return self.s == other.s
    
#     def pack(self, enc):
#         enc.write_bytes(self.raw)
#         return len(self.raw)
    
#     @classmethod
#     def unpack(cls, dec):
#         raw = dec.read_bytes(8)
#         return Name(eos.b2s(raw), raw)

#    def to_bytes(self):
#        return self.raw

class F128(object):
    def __init__(self, raw: bytes):
        assert len(raw) == 16
        self.raw = raw

    def __repr__(self):
        return self.raw.hex()

    def __eq__(self, other):
        return self.raw == other.raw

    def pack(self, enc):
        enc.write_bytes(self.raw)
        return 16

    def get_bytes(self):
        return self.raw

    @classmethod
    def unpack(cls, dec):
        raw = dec.read_bytes(16)
        return F128(raw)

class Checksum256(object):
    def __init__(self, raw: bytes):
        assert len(raw) == 32
        self.raw = raw

    def __repr__(self):
        return self.raw.hex()

    def __eq__(self, other):
        return self.raw == other.raw

    def to_bytes(self):
        return self.raw

    @classmethod
    def from_str(cls, s: str):
        assert len(s) == 64
        return Checksum256(bytes.fromhex(s))

    def pack(self, enc) -> int:
        enc.write_bytes(self.raw)
        return 32

    @classmethod
    def unpack(cls, dec):
        raw = dec.read_bytes(32)
        return Checksum256(raw)

class PublicKey(object):

    def __init__(self, raw: bytes):
        assert len(raw) == 34
        self.raw = raw

    def __repr__(self):
        return self.to_string()

    def __eq__(self, other) -> bool:
        return self.raw == other.raw

    def to_string(self):
        hash = hashlib.new('ripemd160')
        hash.update(self.raw[1:])
        ret = b'EOS' + base58.b58encode(self.raw[1:] + hash.digest()[:4])
        return ret.decode()

    @classmethod
    def from_base58(cls, pub: str):
        return PublicKey(b'\x00' + base58.b58decode(pub[3:])[:-4])

    def pack(self, enc):
        enc.write_bytes(self.raw)
        return 34

    @classmethod
    def unpack(cls, dec):
        raw =  dec.read_bytes(34)
        return PublicKey(raw)
