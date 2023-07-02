# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool
from libc.stdlib cimport malloc
from libc.stdlib cimport free
from cpython.bytes cimport PyBytes_AsStringAndSize, PyBytes_FromStringAndSize

cdef extern from * :
    ctypedef long long int64_t
    ctypedef unsigned long long uint64_t
    ctypedef int int32_t
    ctypedef unsigned int uint32_t
    ctypedef unsigned short uint16_t
    ctypedef unsigned char uint8_t

cdef extern from "_ipyeos.hpp":
    ctypedef struct database_proxy:
        int32_t set_data_handler(int32_t (*)(int32_t tp, char *data, size_t size, void* custom_data), void *custom_data)
        int32_t walk(void *db, int32_t tp, int32_t index_position)
        int32_t walk_range(void *db, int32_t tp, int32_t index_position, char *raw_lower_bound, size_t raw_lower_bound_size, char *raw_upper_bound, size_t raw_upper_bound_size)
        int32_t find(void *db, int32_t tp, int32_t index_position, char *raw_data, size_t size, vector[char] &out)
        
        int32_t create(void *_db, int32_t tp, const char *raw_data, size_t raw_data_size)
        int32_t modify(void *_db, int32_t tp, int32_t index_position, char *raw_key, size_t raw_key_size, char *raw_data, size_t raw_data_size)

        int32_t lower_bound(void *db, int32_t tp, int32_t index_position, char *raw_data, size_t size, vector[char] &out)
        int32_t upper_bound(void *db, int32_t tp, int32_t index_position, char *raw_data, size_t size, vector[char] &out)

        uint64_t row_count(void *db, int32_t tp)

    ctypedef struct ipyeos_proxy:
        void *new_database_proxy()

    ipyeos_proxy *get_ipyeos_proxy() nogil

ctypedef struct python_custom_data:
    void *cb
    void *custom_data

cdef int32_t database_on_data(int32_t tp, char *data, size_t size, void *custom_data):
    cdef python_custom_data *_data = <python_custom_data *>custom_data
    _cb = <object>_data.cb
    _custom_dta = <object>_data.custom_data
    return _cb(tp, PyBytes_FromStringAndSize(data, size), _custom_dta)

cdef database_proxy *db(uint64_t ptr):
    return <database_proxy*>ptr

def new() -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().new_database_proxy()

def create(uint64_t ptr, uint64_t db_ptr, int32_t tp, raw_data: bytes):
    return db(ptr).create(<void *>db_ptr, tp, <const char *>raw_data, len(raw_data))

def modify(uint64_t ptr, uint64_t db_ptr, int32_t tp, int32_t index_position, raw_key: bytes, raw_data: bytes):
    return db(ptr).modify(<void *>db_ptr, tp, index_position, <const char *>raw_key, len(raw_key), <const char *>raw_data, len(raw_data))

def walk(uint64_t ptr, uint64_t db_ptr, tp: int32_t, index_position: int32_t, cb, custom_data: object):
    cdef python_custom_data data
    data.cb = <void *>cb
    data.custom_data = <void *>custom_data
    db(ptr).set_data_handler(database_on_data, <void *>&data)
    return db(ptr).walk(<void *>db_ptr, tp, index_position)

def walk_range(uint64_t ptr, uint64_t db_ptr, tp: int32_t, index_position: int32_t, raw_lower_bound: bytes, raw_upper_bound: bytes, cb, custom_data: object):
    cdef python_custom_data data

    data.cb = <void *>cb
    data.custom_data = <void *>custom_data
    db(ptr).set_data_handler(database_on_data, <void *>&data)

    ret = db(ptr).walk_range(<void *>db_ptr, tp, index_position, <const char *>raw_lower_bound, len(raw_lower_bound), <const char *>raw_upper_bound, len(raw_upper_bound))
    return ret

def find(uint64_t ptr, uint64_t db_ptr, tp: int32_t, index_position: int32_t, raw_data: bytes):
    cdef vector[char] out

    ret = db(ptr).find(<void *>db_ptr, tp, index_position, <const char *>raw_data, len(raw_data), out)
    if ret <= 0:
        return (ret, None)

    raw_data = PyBytes_FromStringAndSize(out.data(), out.size())
    return (ret, raw_data)


def lower_bound(uint64_t ptr, uint64_t db_ptr, tp: int32_t, index_position: int32_t, raw_data: bytes):
    cdef vector[char] out

    ret = db(ptr).lower_bound(<void *>db_ptr, tp, index_position, <const char *>raw_data, len(raw_data), out)
    if ret <= 0:
        return (ret, None)

    raw_data = PyBytes_FromStringAndSize(out.data(), out.size())
    return (ret, raw_data)

def upper_bound(uint64_t ptr, uint64_t db_ptr, tp: int32_t, index_position: int32_t, raw_data: bytes):
    cdef vector[char] out

    ret = db(ptr).upper_bound(<void *>db_ptr, tp, index_position, <const char *>raw_data, len(raw_data), out)
    if ret <= 0:
        return (ret, None)

    raw_data = PyBytes_FromStringAndSize(out.data(), out.size())
    return (ret, raw_data)

def row_count(uint64_t ptr, uint64_t db_ptr, tp: int32_t):
    return db(ptr).row_count(<void *>db_ptr, tp)
