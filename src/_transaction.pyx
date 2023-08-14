# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from typing import Union, List
from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":
    ctypedef struct signed_transaction_ptr:
        pass

    ctypedef struct transaction_proxy:
        void *new_transaction(uint32_t expiration, const char *ref_block_id, size_t ref_block_id_size, uint32_t max_net_usage_words, uint8_t  max_cpu_usage_ms, uint32_t delay_sec)
        void id(vector[char]& _id)
        void add_action(uint64_t account, uint64_t name, const char *data, size_t size, vector[pair[uint64_t, uint64_t]]& auths)
        bool sign(const char *private_key, size_t size, const char *chain_id, size_t chain_id_size)
        void pack(bool compress, vector[char]& packed_transaction)
        bool unpack(const char *packed_transaction, size_t size, int result_type, string& result)

    ctypedef struct ipyeos_proxy:
        transaction_proxy *transaction_proxy_new(
            uint32_t expiration,
            const char* ref_block_id,
            size_t ref_block_id_size,
            uint32_t max_net_usage_words, # fc::unsigned_int
            uint8_t  max_cpu_usage_ms,    #
            uint32_t delay_sec            # fc::unsigned_int
        )
        transaction_proxy *transaction_proxy_new_ex(signed_transaction_ptr *transaction_ptr)
        bool transaction_proxy_free(void *transaction_proxy_ptr)

    ipyeos_proxy *get_ipyeos_proxy()

cdef transaction_proxy *proxy(uint64_t ptr):
    return <transaction_proxy *><void *>ptr

def new_transaction(uint32_t expiration, ref_block_id: bytes, uint32_t max_net_usage_words, uint8_t  max_cpu_usage_ms, uint32_t delay_sec) -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().transaction_proxy_new(expiration, <const char *>ref_block_id, len(ref_block_id), max_net_usage_words, max_cpu_usage_ms, delay_sec)

def attach_transaction(uint64_t ptr) -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().transaction_proxy_new_ex(<signed_transaction_ptr *>ptr)

def free_transaction(uint64_t ptr):
    get_ipyeos_proxy().transaction_proxy_free(<void *>ptr)

def id(uint64_t ptr) -> bytes:
    cdef vector[char] _id
    proxy(ptr).id(_id)
    return PyBytes_FromStringAndSize(_id.data(), _id.size())

def add_action(uint64_t ptr, uint64_t account, uint64_t name, data: bytes, auths: List):
    cdef vector[pair[uint64_t, uint64_t]] _auths
    _auths.resize(len(auths))
    for i in range(len(auths)):
        auth = auths[i]
        _auths[i] = pair[uint64_t, uint64_t](auth[0], auth[1])
    proxy(ptr).add_action(account, name, <const char *>data, len(data), _auths)

def sign(uint64_t ptr, private_key: bytes, chain_id: bytes) -> bool:
    return proxy(ptr).sign(<const char *>private_key, len(private_key), <const char *>chain_id, len(chain_id))

def pack(uint64_t ptr, bool compress):
    cdef vector[char] packed_transaction
    proxy(ptr).pack(compress, packed_transaction)
    return PyBytes_FromStringAndSize(packed_transaction.data(), packed_transaction.size())

cdef transaction_proxy *s_proxy = NULL

cdef transaction_proxy *get_instance():
    global s_proxy
    if s_proxy == NULL:
        s_proxy = get_ipyeos_proxy().transaction_proxy_new(0, b'\x00' * 32, 32, 0, 0, 0)
    return s_proxy

def unpack(packed_transaction: bytes, int result_type):
    cdef string result
    get_instance().unpack(<const char *>packed_transaction, len(packed_transaction), result_type, result)
    ret = PyBytes_FromStringAndSize(result.c_str(), result.size())
    return ret
