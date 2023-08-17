from .native_modules import _signed_block, _packed_transaction
from .packed_transaction import PackedTransaction

class SignedBlock:
    def __init__(self, signed_block_ptr, attach=False):
        if not signed_block_ptr:
            raise ValueError("SignedBlock pointer cannot be null")
        if not attach:
            self._ptr = _signed_block.new(signed_block_ptr)
        else:
            self._ptr = _signed_block.attach(signed_block_ptr)

    @classmethod
    def new(cls, signed_block_ptr):
        return cls(signed_block_ptr, attach=False)

    @classmethod
    def attach(cls, signed_block_ptr):
        return cls(signed_block_ptr, attach=True)

    def free(self):
        if not self._ptr:
            return
        _signed_block.free_signed_block(self._ptr)
        self._ptr = None

    def __del__(self):
        self.free()

    def block_num(self):
        return _signed_block.block_num(self._ptr)
    
    def pack(self):
        return _signed_block.pack(self._ptr)

    def transaction_count(self):
        return _signed_block.transactions_size(self._ptr)

    def get_transaction(self, index):
        if index < 0 or index >= self.transaction_count():
            raise IndexError("Index out of range")
        ptr = _packed_transaction.new_from_signed_block(self._ptr, index)
        if not ptr:
            return None
        ret = PackedTransaction.__new__(PackedTransaction)
        ret.ptr = ptr
        ret.json_str = None
        return ret
