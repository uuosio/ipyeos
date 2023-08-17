# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":

    ctypedef struct transaction_trace_ptr:
        pass

    ctypedef struct action_trace_proxy:
        pass

    ctypedef struct transaction_trace_proxy:
        string id()
        uint32_t block_num()
        bool is_onblock()

        string block_time()
        string producer_block_id()
        string receipt()
        int64_t elapsed()
        uint64_t net_usage()
        bool scheduled()
        string account_ram_delta()
        transaction_trace_ptr& failed_dtrx_trace()
        string except_()
        uint64_t error_code()

        action_trace_proxy *get_action_trace(int index)
        bool free_action_trace(action_trace_proxy *_action_trace_proxy)
        int get_action_traces_size()
        vector[char] pack()
        string to_json()

    ctypedef struct ipyeos_proxy:
        transaction_trace_proxy *transaction_trace_proxy_new(transaction_trace_ptr *_transaction_trace_ptr, bool attach)
        transaction_trace_proxy *transaction_trace_proxy_new_ex(const char *raw_packed_transaction_trace, size_t raw_packed_transaction_trace_size)
        bool transaction_trace_proxy_free(transaction_trace_proxy *transaction_trace_proxy_ptr)

    ipyeos_proxy *get_ipyeos_proxy() nogil

cdef transaction_trace_proxy *proxy(uint64_t ptr):
    return <transaction_trace_proxy*>ptr

def new(uint64_t ptr, bool attach):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return <uint64_t>_proxy.transaction_trace_proxy_new(<transaction_trace_ptr *>ptr, attach)

def new_ex(raw_packed_transaction_trace: bytes):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return <uint64_t>_proxy.transaction_trace_proxy_new_ex(<char *>raw_packed_transaction_trace, len(raw_packed_transaction_trace))

def free_transaction_trace(uint64_t ptr):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return _proxy.transaction_trace_proxy_free(<transaction_trace_proxy*>ptr)

def id(uint64_t ptr):
    return proxy(ptr).id()

def block_num(uint64_t ptr):
    return proxy(ptr).block_num()

def is_onblock(uint64_t ptr):
    return proxy(ptr).is_onblock()

def block_time(uint64_t ptr) -> str:
    return proxy(ptr).block_time()

def producer_block_id(uint64_t ptr) -> str:
    return proxy(ptr).producer_block_id()

def receipt(uint64_t ptr) -> str:
    return proxy(ptr).receipt()

def elapsed(uint64_t ptr) -> int:
    return proxy(ptr).elapsed()

def net_usage(uint64_t ptr) -> int:
    return proxy(ptr).net_usage()

def scheduled(uint64_t ptr) -> bool:
    return proxy(ptr).scheduled()

def account_ram_delta(uint64_t ptr) -> str:
    return proxy(ptr).account_ram_delta()

def failed_dtrx_trace(uint64_t ptr) -> uint64_t:
    return <uint64_t>&proxy(ptr).failed_dtrx_trace()

def except_(uint64_t ptr) -> str:
    return proxy(ptr).except_()

def error_code(uint64_t ptr) -> int:
    return proxy(ptr).error_code()

def get_action_traces_size(uint64_t ptr) -> int:
    return proxy(ptr).get_action_traces_size()

def get_action_trace(uint64_t ptr, int index) -> uint64_t:
    return <uint64_t>proxy(ptr).get_action_trace(index)

def free_action_trace(uint64_t ptr, uint64_t _action_trace_proxy):
    return proxy(ptr).free_action_trace(<action_trace_proxy*>_action_trace_proxy)

# vector<char> pack()
def pack(uint64_t ptr) -> bytes:
    cdef vector[char] _vector = proxy(ptr).pack()
    return PyBytes_FromStringAndSize(<char *>_vector.data(), _vector.size())

# string to_json()
def to_json(uint64_t ptr) -> str:
    return proxy(ptr).to_json()
