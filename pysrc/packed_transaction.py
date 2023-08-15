import json
from typing import Dict, List, Union, Optional

from .native_modules import _packed_transaction
from .signed_transaction import SignedTransaction
from . import eos

from .chain_exceptions import get_last_exception
from .packer import Packer
from .types import I64, U8, U16, U32, U64, Checksum256, Name, PrivateKey

class PackedTransaction(object):
    def __init__(self, ptr, attach = False):
        self.ptr = _packed_transaction.new(ptr, attach)
        self.json_str = None

    def __repr__(self):
        return self.to_json()

    def __str__(self):
        return self.to_json()

    @classmethod
    def attach(cls, signed_transaction_ptr: int):
        return cls(signed_transaction_ptr, True)

    @classmethod
    def from_raw(cls, raw_packed_tx: bytes):
        ptr = _packed_transaction.new_ex(raw_packed_tx)
        if not ptr:
            raise get_last_exception()
        ret = cls.__new__(cls)
        ret.ptr = ptr
        ret.json_str = None
        return ret

    def free(self):
        if not self.ptr:
            return
        _packed_transaction.free_transaction(self.ptr)
        self.ptr = 0

    def __del__(self):
        self.free()

    def get_signed_transaction(self):
        ptr = _packed_transaction.get_signed_transaction(self.ptr)
        return SignedTransaction.attach(ptr)

    def pack(self) -> bytes:
        return _packed_transaction.pack(self.ptr)

    def to_json(self) -> str:
        assert self.ptr, "PackedTransaction is null"
        if not self.json_str:
            self.json_str = _packed_transaction.to_json(self.ptr)
        return self.json_str
