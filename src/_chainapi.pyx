# cython: c_string_type=str, c_string_encoding=ascii

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool
from libc.stdlib cimport malloc


cdef extern from * :
    ctypedef long long int64_t
    ctypedef unsigned long long uint64_t
    ctypedef unsigned int uint32_t
    ctypedef unsigned short uint16_t
    ctypedef unsigned char uint8_t
    ctypedef int __uint128_t

cdef extern from "<Python.h>":
    ctypedef long long PyLongObject

    object PyBytes_FromStringAndSize(const char* str, int size)
    int _PyLong_AsByteArray(PyLongObject* v, unsigned char* bytes, size_t n, int little_endian, int is_signed)

cdef extern from "<uuos.hpp>":
    void uuosext_init()

    ctypedef struct chain_rpc_api_proxy:
        int get_info(string& result)
        int get_account(string& params, string& result)

    ctypedef struct chain_proxy:
        chain_rpc_api_proxy* api_proxy()

    chain_rpc_api_proxy *chain_api(uint64_t ptr)

def get_info(uint64_t ptr):
    cdef string result
    ret = chain_api(ptr).get_info(result)
    return ret, result

def get_account(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_account(params, result)
    return ret, result
