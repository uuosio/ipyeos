from .native_modules import _signed_block

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