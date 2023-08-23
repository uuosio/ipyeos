# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from typing import Union, List
from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":
    ctypedef struct signed_transaction_ptr:
        pass

    ctypedef struct signed_transaction_proxy:
        string first_authorizer()
        void id(vector[char]& _id)
        void add_action(uint64_t account, uint64_t name, const char *data, size_t size, vector[pair[uint64_t, uint64_t]]& auths)
        bool sign(const char *private_key, size_t size, const char *chain_id, size_t chain_id_size)
        void pack(bool compress, int pack_type, vector[char]& packed_transaction)
        bool to_json(int result_type, bool compressed, string& result)

    ctypedef struct ipyeos_proxy:
        signed_transaction_proxy *transaction_proxy_new(
            uint32_t expiration,
            const char* ref_block_id,
            size_t ref_block_id_size,
            uint32_t max_net_usage_words, # fc::unsigned_int
            uint8_t  max_cpu_usage_ms,    #
            uint32_t delay_sec            # fc::unsigned_int
        )
        signed_transaction_proxy *transaction_proxy_new_ex(signed_transaction_ptr *transaction_ptr)
        bool transaction_proxy_free(void *transaction_proxy_ptr)

    ipyeos_proxy *get_ipyeos_proxy()

cdef signed_transaction_proxy *proxy(uint64_t ptr):
    return <signed_transaction_proxy *><void *>ptr

def new_transaction(uint32_t expiration, ref_block_id: bytes, uint32_t max_net_usage_words, uint8_t  max_cpu_usage_ms, uint32_t delay_sec) -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().transaction_proxy_new(expiration, <const char *>ref_block_id, len(ref_block_id), max_net_usage_words, max_cpu_usage_ms, delay_sec)

def attach_transaction(uint64_t ptr) -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().transaction_proxy_new_ex(<signed_transaction_ptr *>ptr)

def free_transaction(uint64_t ptr):
    get_ipyeos_proxy().transaction_proxy_free(<void *>ptr)

def first_authorizer(uint64_t ptr) -> str:
    return proxy(ptr).first_authorizer()
 
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

def pack(uint64_t ptr, bool compress, int pack_type):
    cdef vector[char] packed_transaction
    proxy(ptr).pack(compress, pack_type, packed_transaction)
    return PyBytes_FromStringAndSize(packed_transaction.data(), packed_transaction.size())

def to_json(uint64_t ptr, int result_type, bool compressed):
    cdef string result
    proxy(ptr).to_json(result_type, compressed, result)
    return result

