from .native_modules import _block_state

class BlockState:
    def __init__(self, block_state_proxy_ptr):
        self._ptr = _block_state.new(block_state_proxy_ptr)
    
    def free(self):
        if not self._ptr:
            return
        _block_state.free(self._ptr)
        self._ptr = None

    def __del__(self):
        self.free()

    def get_block_num(self):
        return _block_state.get_block_num(self._ptr)