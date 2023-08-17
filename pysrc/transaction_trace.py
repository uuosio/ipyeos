from .action_trace import ActionTrace
from .native_modules import _transaction_trace
from .chain_exceptions import get_last_exception

class TransactionTrace:
    def __init__(self, tx_trace_ptr, attach = False):
        self._ptr = None
        if not tx_trace_ptr:
            raise Exception("invalid tx_trace_ptr")
        self._ptr = _transaction_trace.new(tx_trace_ptr, attach)
    
    def free(self):
        if not self._ptr:
            return
        _transaction_trace.free_transaction_trace(self._ptr)
        self._ptr = None

    def __del__(self):
        self.free()

    def __repr__(self):
        return self.to_json()

    def __str__(self):
        return self.to_json()

    @classmethod
    def from_raw(cls, data: bytes):
        ret = cls.__new__(cls)
        ret._ptr = _transaction_trace.new_ex(data)
        if not ret._ptr:
            raise get_last_exception()
        return ret

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
        if index >= self.get_action_traces_size():
            raise IndexError("Index out of range")
        return ActionTrace(self._ptr, index)

    def pack(self) -> bytes:
        return _transaction_trace.pack(self._ptr)

    def to_json(self) -> str:
        return _transaction_trace.to_json(self._ptr)
