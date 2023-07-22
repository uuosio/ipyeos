import hashlib
from typing import NewType

from . import eos, log

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

    def to_string(self):
        return self.raw.hex()

    @classmethod
    def empty(cls):
        return Checksum256(bytes(32))

    @classmethod
    def from_string(cls, s: str):
        assert len(s) == 64, f'invalid checksum256 string: length is {len(s)}, should be 64'
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

    def to_bytes(self):
        return self.raw

    @classmethod
    def empty(cls):
        return PublicKey(bytes(34))

    def to_base58(self):
        digest = eos.ripemd160(self.raw[1:])
        ret = 'EOS' + eos.bytes_to_base58(self.raw[1:] + digest[:4])
        return ret

    @classmethod
    def from_base58(cls, pub: str):
        assert pub.startswith('EOS')
        pub = eos.base58_to_bytes(pub[3:])
        assert len(pub) == 37
        digest = eos.ripemd160(pub[:-4])
        assert pub[-4:] == digest[:4]
        return cls(b'\x00' + pub[:-4])

    def pack(self, enc):
        enc.write_bytes(self.raw)
        return 34

    @classmethod
    def unpack(cls, dec):
        raw =  dec.read_bytes(34)
        return cls(raw)

class PrivateKey(object):

    def __init__(self, raw: bytes):
        assert len(raw) == 33
        self.raw = raw

    def to_bytes(self):
        return self.raw

    def __repr__(self):
        return self.to_base58()

    def __eq__(self, other) -> bool:
        return self.raw == other.raw

    def to_base58(self):
        hash = hashlib.sha256()
        raw = b'\x80' + self.raw[1:]
        hash.update(raw)
        digest = hash.digest()
        hash = hashlib.sha256()
        hash.update(digest)
        digest = hash.digest()
        ret = eos.bytes_to_base58(raw + hash.digest()[:4])
        return ret

    @classmethod
    def from_base58(cls, pub: str):
        pub = eos.base58_to_bytes(pub)
        assert len(pub) == 37
        h = hashlib.sha256()
        h.update(pub[:-4])
        digest = h.digest()
        h = hashlib.sha256()
        h.update(digest)
        digest = h.digest()
        assert pub[-4:] == digest[:4], f'invalid checksum: {pub[-4:]} != {digest[:4]}'
        return cls(b'\x00' + pub[1:-4])

    def pack(self, enc):
        enc.write_bytes(self.raw)
        return 34

    @classmethod
    def unpack(cls, dec):
        raw =  dec.read_bytes(34)
        assert raw[0] == 0x00, f'invalid private key type: {raw[0]}'
        return cls(raw)

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
        digest = eos.ripemd160(self.raw[1:] + b'K1')
        ret = 'SIG_K1_' + eos.bytes_to_base58(self.raw[1:] + digest[:4])
        return ret
 
    @classmethod
    def from_base58(cls, sig: str):
        if not sig.startswith('SIG_K1_'):
            raise Exception('Signature should start with SIG_K1_')
        sig = sig[7:]
        sig = eos.base58_to_bytes(sig)
        assert len(sig) == 65+4
        digest = eos.ripemd160(sig[:65] + b'K1')
        if digest[:4] != sig[65:]:
            raise Exception('Checksum mismatch')

        return cls(b'\x00' + sig[:65])

    @classmethod
    def empty(cls):
        return cls(bytes(66))