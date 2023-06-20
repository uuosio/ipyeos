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
        int32_t set_data_handler(int32_t (*)(int32_t tp, char *data, size_t size, void* custom_data), void *custom_data)
        int32_t walk(void *db, int32_t tp, int32_t index_position)
        int32_t walk_range(void *db, int32_t tp, int32_t index_position, char *raw_lower_bound, size_t raw_lower_bound_size, char *raw_upper_bound, size_t raw_upper_bound_size)
        int32_t find(void *db, int32_t tp, int32_t index_position, char *raw_data, size_t size, char **out, size_t *out_size)
        
        int32_t create(void *_db, int32_t tp, const char *raw_data, size_t raw_data_size)
        int32_t modify(void *_db, int32_t tp, int32_t index_position, char *raw_key, size_t raw_key_size, char *raw_data, size_t raw_data_size)

        int32_t lower_bound(void *db, int32_t tp, int32_t index_position, char *raw_data, size_t size, char **out, size_t *out_size)
        int32_t upper_bound(void *db, int32_t tp, int32_t index_position, char *raw_data, size_t size, char **out, size_t *out_size)

        uint64_t row_count(void *db, int32_t tp)

    ctypedef struct ipyeos_proxy:
        void *new_database_proxy()

    ipyeos_proxy *get_ipyeos_proxy() nogil

cdef int32_t database_on_data(int32_t tp, char *data, size_t size, void* handler):
    _handler = <object>handler
    return _handler(tp, PyBytes_FromStringAndSize(data, size))

cdef database_proxy *db(uint64_t ptr):
    return <database_proxy*>ptr

def new() -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().new_database_proxy()

def create(ptr: uint64_t, db_ptr: uint64_t, int32_t tp, raw_data: bytes):
    cdef char *_raw_data
    cdef Py_ssize_t _raw_data_size

    PyBytes_AsStringAndSize(raw_data, &_raw_data, &_raw_data_size)
    return db(ptr).create(<void *>db_ptr, tp, _raw_data, _raw_data_size)

def modify(ptr: uint64_t, db_ptr: uint64_t, int32_t tp, int32_t index_position, raw_key: bytes, raw_data: bytes):
    cdef char *_raw_key
    cdef Py_ssize_t _raw_key_size
    cdef char *_raw_data
    cdef Py_ssize_t _raw_data_size

    PyBytes_AsStringAndSize(raw_key, &_raw_key, &_raw_key_size)
    PyBytes_AsStringAndSize(raw_data, &_raw_data, &_raw_data_size)

    return db(ptr).modify(<void *>db_ptr, tp, index_position, _raw_key, _raw_key_size, _raw_data, _raw_data_size)

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

def find(ptr: uint64_t, db_ptr: uint64_t, tp: int32_t, index_position: int32_t, raw_data: bytes):
    cdef char *_raw_data
    cdef Py_ssize_t _raw_data_length
    cdef char *out
    cdef size_t out_size

    PyBytes_AsStringAndSize(raw_data, &_raw_data, &_raw_data_length)
    ret = db(ptr).find(<void *>db_ptr, tp, index_position, _raw_data, _raw_data_length, &out, &out_size)
    if ret <= 0:
        return (ret, None)

    raw_data = PyBytes_FromStringAndSize(out, out_size)
    return (ret, raw_data)


def lower_bound(ptr: uint64_t, db_ptr: uint64_t, tp: int32_t, index_position: int32_t, raw_data: bytes):
    cdef char *_raw_data
    cdef Py_ssize_t _raw_data_length
    cdef char *out
    cdef size_t out_size

    PyBytes_AsStringAndSize(raw_data, &_raw_data, &_raw_data_length)
    ret = db(ptr).lower_bound(<void *>db_ptr, tp, index_position, _raw_data, _raw_data_length, &out, &out_size)
    if ret <= 0:
        return (ret, None)

    raw_data = PyBytes_FromStringAndSize(out, out_size)
    return (ret, raw_data)

def upper_bound(ptr: uint64_t, db_ptr: uint64_t, tp: int32_t, index_position: int32_t, raw_data: bytes):
    cdef char *_raw_data
    cdef Py_ssize_t _raw_data_length
    cdef char *out
    cdef size_t out_size

    PyBytes_AsStringAndSize(raw_data, &_raw_data, &_raw_data_length)
    ret = db(ptr).upper_bound(<void *>db_ptr, tp, index_position, _raw_data, _raw_data_length, &out, &out_size)
    if ret <= 0:
        return (ret, None)

    raw_data = PyBytes_FromStringAndSize(out, out_size)
    return (ret, raw_data)

def row_count(ptr: uint64_t, db_ptr: uint64_t, tp: int32_t):
    return db(ptr).row_count(<void *>db_ptr, tp)
