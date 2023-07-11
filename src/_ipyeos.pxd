from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp.pair cimport pair
from libcpp cimport bool
from libc.stdlib cimport malloc
from libc.string cimport memcpy
from libc.string cimport memset
from libc.stdlib cimport free
from cpython.bytes cimport PyBytes_AsStringAndSize, PyBytes_FromStringAndSize

cdef extern from * :
    ctypedef long long int64_t
    ctypedef unsigned long long uint64_t
    ctypedef int int32_t
    ctypedef unsigned int uint32_t
    ctypedef unsigned short uint16_t
    ctypedef unsigned char uint8_t
