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

    @staticmethod
    def attach(cls, signed_transaction_ptr: int):
        return cls(signed_transaction_ptr, True)

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
