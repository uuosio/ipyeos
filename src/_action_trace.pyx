# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":

    ctypedef struct action_trace_proxy:
        uint32_t action_ordinal()
        uint32_t creator_action_ordinal()
        uint32_t closest_unnotified_ancestor_action_ordinal()
        string receipt()
        string receiver()

        string act()
        string get_action_account()
        string get_action_name()
        string get_action_authorization()
        string get_action_data()

        bool context_free()
        uint64_t elapsed()
        string console()
        string trx_id()
        uint32_t block_num()
        string block_time()
        string producer_block_id()
        string account_ram_deltas()
        string except_()
        uint64_t error_code()
        string return_value()

    ctypedef struct transaction_trace_proxy:
        action_trace_proxy *get_action_trace(int index)
        bool free_action_trace(action_trace_proxy *_action_trace_proxy)

cdef action_trace_proxy *proxy(uint64_t ptr):
    return <action_trace_proxy*>ptr

def new(uint64_t _transaction_trace_proxy_ptr, int index):
    cdef transaction_trace_proxy *_proxy = <transaction_trace_proxy *>_transaction_trace_proxy_ptr
    return <uint64_t>_proxy.get_action_trace(index)

def free_action_trace(uint64_t _transaction_trace_proxy_ptr, uint64_t ptr):
    cdef transaction_trace_proxy *_proxy = <transaction_trace_proxy *>_transaction_trace_proxy_ptr
    return _proxy.free_action_trace(<action_trace_proxy*>ptr)


# uint32_t action_ordinal()
def action_ordinal(uint64_t ptr):
    return proxy(ptr).action_ordinal()
# uint32_t creator_action_ordinal()
def creator_action_ordinal(uint64_t ptr):
    return proxy(ptr).creator_action_ordinal()
# uint32_t closest_unnotified_ancestor_action_ordinal()
def closest_unnotified_ancestor_action_ordinal(uint64_t ptr):
    return proxy(ptr).closest_unnotified_ancestor_action_ordinal()
# string receipt()
def receipt(uint64_t ptr):
    return proxy(ptr).receipt()
# string receiver()
def receiver(uint64_t ptr):
    return proxy(ptr).receiver()
# string act()
def act(uint64_t ptr):
    return proxy(ptr).act()
# string get_action_account()
def get_action_account(uint64_t ptr):
    return proxy(ptr).get_action_account()
# string get_action_name()
def get_action_name(uint64_t ptr):
    return proxy(ptr).get_action_name()
# string get_action_authorization()
def get_action_authorization(uint64_t ptr):
    return proxy(ptr).get_action_authorization()
# string get_action_data()
def get_action_data(uint64_t ptr):
    return proxy(ptr).get_action_data()
# bool context_free()
def context_free(uint64_t ptr):
    return proxy(ptr).context_free()
# uint64_t elapsed()
def elapsed(uint64_t ptr):
    return proxy(ptr).elapsed()
# string console()
def console(uint64_t ptr):
    return proxy(ptr).console()
# string trx_id()
def trx_id(uint64_t ptr):
    return proxy(ptr).trx_id()
# uint32_t block_num()
def block_num(uint64_t ptr):
    return proxy(ptr).block_num()
# string block_time()
def block_time(uint64_t ptr):
    return proxy(ptr).block_time()
# string producer_block_id()
def producer_block_id(uint64_t ptr):
    return proxy(ptr).producer_block_id()
# string account_ram_deltas()
def account_ram_deltas(uint64_t ptr):
    return proxy(ptr).account_ram_deltas()
# string except_()
def except_(uint64_t ptr):
    return proxy(ptr).except_()
# uint64_t error_code()
def error_code(uint64_t ptr):
    return proxy(ptr).error_code()
# string return_value()
def return_value(uint64_t ptr):
    return proxy(ptr).return_value()
