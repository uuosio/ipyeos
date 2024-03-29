from .signed_block import SignedBlock

from ..native_modules import _block_state

class BlockState:
    def __init__(self, block_state_proxy_ptr):
        self._ptr = _block_state.new(block_state_proxy_ptr)
        self._block = None
    
    @classmethod
    def init(cls, block_state_proxy_ptr):
        ret = cls.__new__(cls)
        ret._ptr = block_state_proxy_ptr
        ret._block = None
        return ret

    def free(self):
        if not self._ptr:
            return
        if self._block:
            self._block.free()
            self._block = None
        _block_state.free_block_state(self._ptr)
        self._ptr = None

    def __del__(self):
        self.free()

    def block_num(self):
        return _block_state.block_num(self._ptr)

    def block(self):
        if not self._block:
            signed_block_ptr = _block_state.block(self._ptr)
            self._block = SignedBlock(signed_block_ptr)
        return self._block
