# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":

    ctypedef struct read_write_lock_proxy:
        void acquire_read_lock() nogil
        void release_read_lock() nogil
        void acquire_write_lock() nogil
        void release_write_lock() nogil

    ctypedef struct ipyeos_proxy:
        read_write_lock_proxy* read_write_lock_proxy_new(const string& mutex_name)
        bool read_write_lock_proxy_free(void *ptr)

    ipyeos_proxy *get_ipyeos_proxy() nogil

cdef read_write_lock_proxy *proxy(uint64_t ptr):
    return <read_write_lock_proxy*>ptr

def new(const string& mutex_name):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return <uint64_t>_proxy.read_write_lock_proxy_new(mutex_name)

def free(uint64_t ptr):
    cdef ipyeos_proxy *_proxy = get_ipyeos_proxy()
    return _proxy.read_write_lock_proxy_free(<void*>ptr)

def acquire_read_lock(uint64_t ptr):
    proxy(ptr).acquire_read_lock()

def release_read_lock(uint64_t ptr):
    proxy(ptr).release_read_lock()

def acquire_write_lock(uint64_t ptr):
    proxy(ptr).acquire_write_lock()

def release_write_lock(uint64_t ptr):
    proxy(ptr).release_write_lock()
