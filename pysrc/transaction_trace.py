from .action_trace import ActionTrace
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

# string block_time()
    def block_time(self):
        return _transaction_trace.block_time(self._ptr)
# string producer_block_id()
    def producer_block_id(self):
        return _transaction_trace.producer_block_id(self._ptr)
# string receipt()
    def receipt(self):
        return _transaction_trace.receipt(self._ptr)
# int64_t elapsed()
    def elapsed(self):
        return _transaction_trace.elapsed(self._ptr)

# uint64_t net_usage()
    def net_usage(self):
        return _transaction_trace.net_usage(self._ptr)
# bool scheduled()
    def scheduled(self):
        return _transaction_trace.scheduled(self._ptr)
# string account_ram_delta()
    def account_ram_delta(self):
        return _transaction_trace.account_ram_delta(self._ptr)
# transaction_trace_ptr& failed_dtrx_trace()
    def failed_dtrx_trace(self):
        ptr = _transaction_trace.failed_dtrx_trace(self._ptr)
        return TransactionTrace(ptr, False)
# string except_()
    def except_(self):
        return _transaction_trace.except_(self._ptr)
# uint64_t error_code()
    def error_code(self):
        return _transaction_trace.error_code(self._ptr)

    def get_action_traces_size(self):
        return _transaction_trace.get_action_traces_size(self._ptr)

    def get_action_trace(self, index: int):
        return ActionTrace(self._ptr, index)
