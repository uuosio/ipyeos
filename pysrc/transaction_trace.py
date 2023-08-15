from .native_modules import _transaction_trace

class TransactionTrace:
    def __init__(self, tx_trace_ptr, attach = False):
        self._ptr = _transaction_trace.new(tx_trace_ptr, attach)
    
    def free(self):
        if not self._ptr:
            return
        _transaction_trace.free_transaction_trace(self._ptr)
        self._ptr = None

    def __del__(self):
        self.free()

    def block_num(self):
        return _transaction_trace.block_num(self._ptr)

    def is_onblock(self):
        return _transaction_trace.is_onblock(self._ptr)
