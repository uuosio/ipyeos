# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from typing import Union, List
from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":
    ctypedef struct transaction_proxy:
        void *new_transaction(uint32_t expiration, const char *ref_block_id, size_t ref_block_id_size, uint32_t max_net_usage_words, uint8_t  max_cpu_usage_ms, uint32_t delay_sec);
        void free(void *transaction)
        void id(void *transaction, vector[char]& _id)
        void add_action(void *transaction, uint64_t account, uint64_t name, const char *data, size_t size, vector[pair[uint64_t, uint64_t]]& auths);
        bool sign(void *transaction, const char *private_key, size_t size, const char *chain_id, size_t chain_id_size);
        void pack(void *transaction, bool compress, vector[char]& packed_transaction);
        bool unpack(const char *packed_transaction, size_t size, int result_type, string& result);


    ctypedef struct ipyeos_proxy:
        transaction_proxy* get_transaction_proxy()

    ipyeos_proxy *get_ipyeos_proxy()
    transaction_proxy *get_transaction_proxy()

def new_transaction(uint32_t expiration, ref_block_id: bytes, uint32_t max_net_usage_words, uint8_t  max_cpu_usage_ms, uint32_t delay_sec) -> uint64_t:
    return <uint64_t>get_transaction_proxy().new_transaction(expiration, <const char *>ref_block_id, len(ref_block_id), max_net_usage_words, max_cpu_usage_ms, delay_sec)

def free(uint64_t ptr):
    get_transaction_proxy().free(<void *>ptr)

def id(uint64_t ptr) -> bytes:
    cdef vector[char] _id
    get_transaction_proxy().id(<void *>ptr, _id)
    return PyBytes_FromStringAndSize(_id.data(), _id.size())

def add_action(uint64_t ptr, uint64_t account, uint64_t name, data: bytes, auths: List):
    cdef vector[pair[uint64_t, uint64_t]] _auths
    _auths.resize(len(auths))
    for i in range(len(auths)):
        auth = auths[i]
        _auths[i] = pair[uint64_t, uint64_t](auth[0], auth[1])
    get_transaction_proxy().add_action(<void *>ptr, account, name, <const char *>data, len(data), _auths)

def sign(uint64_t ptr, private_key: bytes, chain_id: bytes) -> bool:
    return get_transaction_proxy().sign(<void *>ptr, <const char *>private_key, len(private_key), <const char *>chain_id, len(chain_id))

def pack(uint64_t ptr, bool compress):
    cdef vector[char] packed_transaction
    get_transaction_proxy().pack(<void *>ptr, compress, packed_transaction)
    return PyBytes_FromStringAndSize(packed_transaction.data(), packed_transaction.size())

def unpack(packed_transaction: bytes, int result_type):
    cdef string result
    get_transaction_proxy().unpack(<const char *>packed_transaction, len(packed_transaction), result_type, result)
    return PyBytes_FromStringAndSize(result.c_str(), result.size())
