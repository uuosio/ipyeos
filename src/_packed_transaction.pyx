# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from typing import Union, List
from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":

    ctypedef struct packed_transaction_ptr:
        pass

    ctypedef struct signed_transaction_ptr:
        pass

    ctypedef struct packed_transaction_proxy:
        signed_transaction_ptr *get_signed_transaction()
        vector[char] pack()
        string to_json()

    ctypedef struct ipyeos_proxy:
        packed_transaction_proxy *packed_transaction_proxy_new(packed_transaction_ptr *_packed_transaction_ptr, bool attach)
        packed_transaction_proxy *packed_transaction_proxy_new_ex(const char *raw_packed_tx, size_t raw_packed_tx_size)

        bool packed_transaction_proxy_free(packed_transaction_proxy *packed_transaction_proxy_ptr)

    ipyeos_proxy *get_ipyeos_proxy()

cdef packed_transaction_proxy *proxy(uint64_t ptr):
    return <packed_transaction_proxy *><void *>ptr

def new(uint64_t ptr, bool attach) -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().packed_transaction_proxy_new(<packed_transaction_ptr *>ptr, attach)

def new_ex(raw_packed_tx: bytes) -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().packed_transaction_proxy_new_ex(<char *>raw_packed_tx, len(raw_packed_tx))

def free_transaction(uint64_t ptr):
    get_ipyeos_proxy().packed_transaction_proxy_free(<packed_transaction_proxy *>ptr)

def pack(uint64_t ptr) -> bytes:
    cdef vector[char] packed = proxy(ptr).pack()
    return PyBytes_FromStringAndSize(<char *>packed.data(), packed.size())

def get_signed_transaction(uint64_t ptr) -> uint64_t:
    return <uint64_t>proxy(ptr).get_signed_transaction()

def to_json(uint64_t ptr) -> str:
    return proxy(ptr).to_json()
