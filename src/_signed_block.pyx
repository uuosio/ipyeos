# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":
    ctypedef struct packed_transaction_proxy:
        pass

    ctypedef struct signed_block_ptr:
        pass

    ctypedef struct signed_block_proxy:
        uint32_t block_num()
        vector[char] pack()
        size_t transactions_size()
        vector[char] get_transaction_id(int index)
        bool is_packed_transaction(int index)
        packed_transaction_proxy *get_packed_transaction(int index)
        string to_json()

    ctypedef struct ipyeos_proxy:
        signed_block_proxy *signed_block_proxy_new(signed_block_ptr *_signed_block_ptr)
        signed_block_proxy *signed_block_proxy_new_ex(const char *raw_signed_block, size_t raw_signed_block_size)
        signed_block_proxy *signed_block_proxy_attach(signed_block_ptr *_signed_block_ptr)
        bool signed_block_proxy_free(signed_block_ptr *signed_block_proxy_ptr)

    ipyeos_proxy *get_ipyeos_proxy() nogil

cdef signed_block_proxy *proxy(uint64_t ptr):
    return <signed_block_proxy*>ptr

def new(uint64_t signed_block_proxy_ptr):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return <uint64_t>_proxy.signed_block_proxy_new(<signed_block_ptr *>signed_block_proxy_ptr)

# signed_block_proxy *signed_block_proxy_new_ex(const char *raw_signed_block, size_t raw_signed_block_size)
def new_ex(raw_signed_block: bytes):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return <uint64_t>_proxy.signed_block_proxy_new_ex(<char *>raw_signed_block, len(raw_signed_block))

def attach(uint64_t signed_block_proxy_ptr):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return <uint64_t>_proxy.signed_block_proxy_attach(<signed_block_ptr *>signed_block_proxy_ptr)

def free_signed_block(uint64_t ptr):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return _proxy.signed_block_proxy_free(<signed_block_ptr*>ptr)

def block_num(uint64_t ptr):
    return proxy(ptr).block_num()

def pack(uint64_t ptr):
    ret = proxy(ptr).pack()
    return PyBytes_FromStringAndSize(<char *>ret.data(), ret.size())

def transactions_size(uint64_t ptr):
    return proxy(ptr).transactions_size()

# vector<char> get_transaction_id(int index)
def get_transaction_id(uint64_t ptr, int index):
    ret = proxy(ptr).get_transaction_id(index)
    return PyBytes_FromStringAndSize(<char *>ret.data(), ret.size())
# bool is_packed_transaction(int index)
def is_packed_transaction(uint64_t ptr, int index):
    return proxy(ptr).is_packed_transaction(index)

# packed_transaction_proxy *get_packed_transaction(int index)
def get_packed_transaction(uint64_t ptr, int index):
    return <uint64_t>proxy(ptr).get_packed_transaction(index)

# string to_json()
def to_json(uint64_t ptr) -> str:
    return proxy(ptr).to_json()
