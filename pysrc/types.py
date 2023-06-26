import hashlib
from typing import NewType
from . import eos

I8 = NewType('I8', int)
U8 = NewType('U8', int)
I16 = NewType('I16', int)
U16 = NewType('U16', int)
I32 = NewType('I32', int)
U32 = NewType('U32', int)
I64 = NewType('I64', int)
U64 = NewType('U64', int)
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
        return self.to_base58()

    def __eq__(self, other) -> bool:
        return self.raw == other.raw

    def to_base58(self):
        hash = hashlib.new('ripemd160')
        hash.update(self.raw[1:])
        ret = 'EOS' + eos.bytes_to_base58(self.raw[1:] + hash.digest()[:4])
        return ret

    @classmethod
    def from_base58(cls, pub: str):
        assert pub.startswith('EOS')
        pub = eos.base58_to_bytes(pub[3:])
        assert len(pub) == 37
        digest = hashlib.new('ripemd160', pub[:-4]).digest()
        assert pub[-4:] == digest[:4]
        return PublicKey(b'\x00' + pub[:-4])

    def pack(self, enc):
        enc.write_bytes(self.raw)
        return 34

    @classmethod
    def unpack(cls, dec):
        raw =  dec.read_bytes(34)
        return PublicKey(raw)

class Signature(object):
    def __init__(self, raw: bytes):
        assert len(raw) == 66, f'Signature should be 66 bytes long, got {len(raw)}'
        self.raw = raw
    
    def pack(self, enc):
        enc.write_bytes(self.raw)
        return 66
    
    @classmethod
    def unpack(cls, dec):
        raw = dec.read_bytes(66)
        return Signature(raw)

    def __repr__(self):
        return self.to_base58()
    
    def __eq__(self, other):
        return self.raw == other.raw
    
    def pack(self, enc):
        enc.write_bytes(self.raw)
        return 66
    
    @classmethod
    def unpack(cls, dec):
        raw = dec.read_bytes(66)
        return Signature(raw)

    def to_base58(self):
        #convert to base58 encoded string
        assert self.raw[0] == 0
        hash = hashlib.new('ripemd160')
        hash.update(self.raw[1:])
        hash.update(b'K1')
        digest = hash.digest()
        ret = 'SIG_K1_' + eos.bytes_to_base58(self.raw[1:] + digest[:4])
        return ret
 
    @classmethod
    def from_base58(cls, sig: str):
        if not sig.startswith('SIG_K1_'):
            raise Exception('Signature should start with SIG_K1_')
        sig = sig[7:]
        sig = eos.base58_to_bytes(sig)
        assert len(sig) == 65+4
        hash = hashlib.new('ripemd160')
        hash.update(sig[:65])
        hash.update(b'K1')
        digest = hash.digest()

        if digest[:4] != sig[65:]:
            raise Exception('Checksum mismatch')

        return Signature(b'\x00' + sig[:65])
