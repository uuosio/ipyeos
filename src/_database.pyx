# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool
from libc.stdlib cimport malloc
from libc.stdlib cimport free

cdef extern from * :
    ctypedef long long int64_t
    ctypedef unsigned long long uint64_t
    ctypedef int int32_t
    ctypedef unsigned int uint32_t
    ctypedef unsigned short uint16_t
    ctypedef unsigned char uint8_t
    ctypedef int __uint128_t

cdef extern from "<Python.h>":
    ctypedef long long PyLongObject

    object PyBytes_FromStringAndSize(const char* str, int size)
    int PyBytes_AsStringAndSize(object obj, char **buffer, Py_ssize_t *length)
    int _PyLong_AsByteArray(PyLongObject* v, unsigned char* bytes, size_t n, int little_endian, int is_signed)

cdef extern from "_ipyeos.hpp":
    void uuosext_init()

    ctypedef struct database_proxy:
        int32_t set_data_handler(int32_t (*)(int32_t tp, int64_t id, char *data, size_t size, void* custom_data), void *custom_data)
        int32_t walk(void *db, int32_t tp, int32_t index_position)
        int32_t walk_range(void *db, int32_t tp, int32_t index_position, char *raw_lower_bound, size_t raw_lower_bound_size, char *raw_upper_bound, size_t raw_upper_bound_size)
        int32_t find(void *db, int32_t tp, int32_t index_position, char *raw_data, size_t size, char *out, size_t out_size)

    ctypedef struct ipyeos_proxy:
        void *new_database_proxy()

    ipyeos_proxy *get_ipyeos_proxy() nogil

cdef int32_t database_on_data(int32_t tp, int64_t id, char *data, size_t size, void* handler):
    _handler = <object>handler
    return _handler(tp, id, PyBytes_FromStringAndSize(data, size))

cdef database_proxy *db(uint64_t ptr):
    return <database_proxy*>ptr

def new() -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().new_database_proxy()

def walk(ptr: uint64_t, db_ptr: uint64_t, tp: int32_t, index_position: int32_t, cb):
    db(ptr).set_data_handler(database_on_data, <void *>cb)
    return db(ptr).walk(<void *>db_ptr, tp, index_position)

def walk_range(ptr: uint64_t, db_ptr: uint64_t, tp: int32_t, index_position: int32_t, cb, raw_lower_bound: bytes, raw_upper_bound: bytes):
    cdef char *_raw_lower_bound
    cdef Py_ssize_t _raw_lower_bound_length
    cdef char *_raw_upper_bound
    cdef Py_ssize_t _raw_upper_bound_length

    PyBytes_AsStringAndSize(raw_lower_bound, &_raw_lower_bound, &_raw_lower_bound_length)
    PyBytes_AsStringAndSize(raw_upper_bound, &_raw_upper_bound, &_raw_upper_bound_length)

    db(ptr).set_data_handler(database_on_data, <void *>cb)

    ret = db(ptr).walk_range(<void *>db_ptr, tp, index_position, _raw_lower_bound, _raw_lower_bound_length, _raw_upper_bound, _raw_upper_bound_length)
    return ret

def find(ptr: uint64_t, db_ptr: uint64_t, tp: int32_t, index_position: int32_t, raw_data: bytes, max_buffer_size):
    cdef char *_raw_data
    cdef Py_ssize_t _raw_data_length
    cdef char *out
    cdef int32_t actual_size

    out = <char *>malloc(max_buffer_size)
    PyBytes_AsStringAndSize(raw_data, &_raw_data, &_raw_data_length)
    ret = db(ptr).find(<void *>db_ptr, tp, index_position, _raw_data, _raw_data_length, out, max_buffer_size)

    if ret < 0:
        return (ret, None)

    real_size = ret
    if real_size > max_buffer_size:
        real_size = max_buffer_size

    raw_data = PyBytes_FromStringAndSize(out, real_size)
    free(out)
    return (ret, raw_data)
