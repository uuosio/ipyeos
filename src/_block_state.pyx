# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":

    ctypedef struct signed_block_ptr:
        pass

    ctypedef struct block_state_proxy:
        uint32_t block_num()
        signed_block_ptr *block()

    ctypedef struct ipyeos_proxy:
        block_state_proxy *block_state_proxy_new(void *block_state_proxy_ptr)
        bool block_state_proxy_free(void *block_state_proxy_ptr)

    ipyeos_proxy *get_ipyeos_proxy() nogil

cdef block_state_proxy *proxy(uint64_t ptr):
    return <block_state_proxy*>ptr

def new(uint64_t ptr):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return <uint64_t>_proxy.block_state_proxy_new(<void *>ptr)

def free_block_state(uint64_t ptr):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return _proxy.block_state_proxy_free(<void*>ptr)

def block_num(uint64_t ptr):
    return proxy(ptr).block_num()

def block(uint64_t ptr):
    return <uint64_t>proxy(ptr).block()

