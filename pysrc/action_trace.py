from .native_modules import _action_trace

class ActionTrace:
    def __init__(self, _transaction_trace_ptr, index: int):
        self._transaction_trace_ptr = _transaction_trace_ptr
        self._ptr = _action_trace.new(_transaction_trace_ptr, index)
    
    def free(self):
        if not self._ptr:
            return
        _action_trace.free_action_trace(self._transaction_trace_ptr, self._ptr)
        self._ptr = None
        self._transaction_trace_ptr = None

    def __del__(self):
        self.free()

    def action_ordinal(self):
        return _action_trace.action_ordinal(self._ptr)

    def creator_action_ordinal(self):
        return _action_trace.creator_action_ordinal(self._ptr)

    def closest_unnotified_ancestor_action_ordinal(self):
        return _action_trace.closest_unnotified_ancestor_action_ordinal(self._ptr)

    def receipt(self):
        return _action_trace.receipt(self._ptr)

    def receiver(self):
        return _action_trace.receiver(self._ptr)

    def act(self):
        return _action_trace.act(self._ptr)

    def get_action_account(self):
        return _action_trace.get_action_account(self._ptr)

    def get_action_name(self):
        return _action_trace.get_action_name(self._ptr)

    def get_action_authorization(self):
        return _action_trace.get_action_authorization(self._ptr)

    def get_action_data(self):
        return _action_trace.get_action_data(self._ptr)

    def context_free(self):
        return _action_trace.context_free(self._ptr)

    def elapsed(self):
        return _action_trace.elapsed(self._ptr)

    def console(self):
        return _action_trace.console(self._ptr)

    def trx_id(self):
        return _action_trace.trx_id(self._ptr)

    def block_num(self):
        return _action_trace.block_num(self._ptr)

    def block_time(self):
        return _action_trace.block_time(self._ptr)

    def producer_block_id(self):
        return _action_trace.producer_block_id(self._ptr)

    def account_ram_deltas(self):
        return _action_trace.account_ram_deltas(self._ptr)

    def except_(self):
        return _action_trace.except_(self._ptr)

    def error_code(self):
        return _action_trace.error_code(self._ptr)

    def return_value(self):
        return _action_trace.return_value(self._ptr)
