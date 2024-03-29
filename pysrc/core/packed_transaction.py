import json
from typing import Dict, List, Union, Optional

from .signed_transaction import SignedTransaction
from .chain_exceptions import get_last_exception


from .. import eos
from ..native_modules import _packed_transaction
from ..bases.packer import Packer
from ..bases.types import I64, U8, U16, U32, U64, Checksum256, Name, PrivateKey

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
    def new_from_signed_transaction(cls, signed_tx: SignedTransaction, compressed: bool = False):
        """
        Initializes a new packed transaction object from a signed transaction object.

        Args:
            signed_tx: The signed transaction object.
            bool compressed: Whether to compress the transaction.

        Returns:
            PackedTransaction: The new packed transaction object.
        """
        assert signed_tx, "signed_tx is null"
        ret = cls.__new__(cls)
        ret.ptr = _packed_transaction.new_from_signed_transaction(signed_tx.ptr, compressed)
        ret.json_str = None
        return ret

    @classmethod
    def unpack(cls, raw_packed_tx: bytes):
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

    def first_authorizer(self) -> str:
        return _packed_transaction.first_authorizer(self.ptr)

    def get_signed_transaction(self):
        ptr = _packed_transaction.get_signed_transaction(self.ptr)
        return SignedTransaction.init(ptr)

    def pack(self) -> bytes:
        return _packed_transaction.pack(self.ptr)

    def to_json(self) -> str:
        assert self.ptr, "PackedTransaction is null"
        if not self.json_str:
            self.json_str = _packed_transaction.to_json(self.ptr)
        return self.json_str
