# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":

    ctypedef struct signed_block_ptr:
        pass

    ctypedef struct signed_block_proxy:
        uint32_t block_num()
        vector[char] pack()

    ctypedef struct ipyeos_proxy:
        signed_block_proxy *signed_block_proxy_new(signed_block_ptr *_signed_block_ptr)
        signed_block_proxy *signed_block_proxy_attach(signed_block_ptr *_signed_block_ptr)
        bool signed_block_proxy_free(signed_block_ptr *signed_block_proxy_ptr)

    ipyeos_proxy *get_ipyeos_proxy() nogil

cdef signed_block_proxy *proxy(uint64_t ptr):
    return <signed_block_proxy*>ptr

def new(uint64_t signed_block_proxy_ptr):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return <uint64_t>_proxy.signed_block_proxy_new(<signed_block_ptr *>signed_block_proxy_ptr)

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
