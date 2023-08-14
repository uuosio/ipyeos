from .native_modules import _signed_block

class SignedBlock:
    def __init__(self, signed_block_ptr):
        self._ptr = _signed_block.new(signed_block_ptr)
    
    def free(self):
        if not self._ptr:
            return
        _signed_block.free(self._ptr)
        self._ptr = None

    def __del__(self):
        self.free()

    def block_num(self):
        return _signed_block.block_num(self._ptr)