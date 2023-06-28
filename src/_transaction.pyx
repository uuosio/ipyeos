# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool
from libcpp.pair cimport pair
from libc.stdlib cimport malloc
from libc.string cimport memcpy
from cpython.bytes cimport PyBytes_AsStringAndSize, PyBytes_FromStringAndSize

from typing import Union, List

cdef extern from * :
    ctypedef long long int64_t
    ctypedef unsigned long long uint64_t
    ctypedef unsigned int uint32_t
    ctypedef int          int32_t
    ctypedef unsigned short uint16_t
    ctypedef unsigned char uint8_t

cdef extern from "_ipyeos.hpp":
    void uuosext_init()

    ctypedef struct transaction_proxy:
        void *new_transaction(uint32_t expiration, uint16_t ref_block_num, uint32_t ref_block_prefix, uint32_t max_net_usage_words, uint8_t  max_cpu_usage_ms, uint32_t delay_sec);
        void free_transaction(void *transaction);
        void add_action(void *transaction, uint64_t account, uint64_t name, const char *data, size_t size, vector[pair[uint64_t, uint64_t]]& auths);
        void sign_transaction(void *transaction, const char *private_key, size_t size);
        void pack_transaction(void *transaction, vector[char]& packed_transaction);

    ctypedef struct ipyeos_proxy:
        transaction_proxy* get_transaction_proxy()

    ipyeos_proxy *get_ipyeos_proxy()
    transaction_proxy *get_transaction_proxy()



#void *new_transaction(uint32_t expiration, uint16_t ref_block_num, uint32_t ref_block_prefix, uint32_t max_net_usage_words, uint8_t  max_cpu_usage_ms, uint32_t delay_sec);
def new_transaction(uint32_t expiration, uint16_t ref_block_num, uint32_t ref_block_prefix, uint32_t max_net_usage_words, uint8_t  max_cpu_usage_ms, uint32_t delay_sec) -> uint64_t:
    return <uint64_t>get_transaction_proxy().new_transaction(expiration, ref_block_num, ref_block_prefix, max_net_usage_words, max_cpu_usage_ms, delay_sec)

#void free_transaction(void *transaction);
def free_transaction(uint64_t ptr):
    get_transaction_proxy().free_transaction(<void *>ptr)

#void add_action(void *transaction, uint64_t account, uint64_t name, const char *data, size_t size, vector[pair[uint64_t, uint64_t]]& auths);
def add_action(uint64_t ptr, uint64_t account, uint64_t name, data: bytes, auths: List):
    cdef vector[pair[uint64_t, uint64_t]] _auths
    _auths.resize(len(auths))
    for i in range(len(auths)):
        auth = auths[i]
        _auths[i] = pair[uint64_t, uint64_t](auth[0], auth[1])
    get_transaction_proxy().add_action(<void *>ptr, account, name, <const char *>data, len(data), _auths)

#void sign_transaction(void *transaction, const char *private_key, size_t size)
def sign_transaction(uint64_t ptr, private_key: bytes):
    get_transaction_proxy().sign_transaction(<void *>ptr, <const char *>private_key, len(private_key))

#void pack_transaction(void *transaction, );
def pack_transaction(uint64_t ptr):
    cdef vector[char] packed_transaction
    get_transaction_proxy().pack_transaction(<void *>ptr, packed_transaction)
    return PyBytes_FromStringAndSize(packed_transaction.data(), packed_transaction.size())
