# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":

    ctypedef struct transaction_trace_ptr:
        pass

    ctypedef struct transaction_trace_proxy:
        uint32_t block_num()
        bool is_onblock()

    ctypedef struct ipyeos_proxy:
        transaction_trace_proxy *transaction_trace_proxy_new(transaction_trace_ptr *_transaction_trace_ptr, bool attach)
        bool transaction_trace_proxy_free(transaction_trace_proxy *transaction_trace_proxy_ptr)

    ipyeos_proxy *get_ipyeos_proxy() nogil

cdef transaction_trace_proxy *proxy(uint64_t ptr):
    return <transaction_trace_proxy*>ptr

def new(uint64_t ptr, bool attach):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return <uint64_t>_proxy.transaction_trace_proxy_new(<transaction_trace_ptr *>ptr, attach)

def free_transaction_trace(uint64_t ptr):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return _proxy.transaction_trace_proxy_free(<transaction_trace_proxy*>ptr)

def block_num(uint64_t ptr):
    return proxy(ptr).block_num()

def is_onblock(uint64_t ptr):
    return proxy(ptr).is_onblock()

