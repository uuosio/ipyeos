# cython: c_string_type=str, c_string_encoding=utf8

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
        int get_info(string& result);
        int get_activated_protocol_features(string& params, string& result);
        int get_block(string& params, string& result);
        int get_block_header_state(string& params, string& result);
        int get_account(string& params, string& result);
        int get_code(string& params, string& result);
        int get_code_hash(string& params, string& result);
        int get_abi(string& params, string& result);
        int get_raw_code_and_abi(string& params, string& result);
        int get_raw_abi(string& params, string& result);
        int get_table_rows(string& params, string& result);
        int get_table_by_scope(string& params, string& result);
        int get_currency_balance(string& params, string& result);
        int get_currency_stats(string& params, string& result);
        int get_producers(string& params, string& result);
        int get_producer_schedule(string& params, string& result);

        int get_scheduled_transactions(string& params, string& result);
        int abi_json_to_bin(string& params, string& result);
        int abi_bin_to_json(string& params, string& result);
        int get_required_keys(string& params, string& result);
        int get_transaction_id(string& params, string& result);

        int get_kv_table_rows(string& params, string& result);


    ctypedef struct chain_proxy:
        chain_rpc_api_proxy* api_proxy()

    chain_rpc_api_proxy *chain_api(uint64_t ptr)

def get_info(uint64_t ptr):
    cdef string result
    ret = chain_api(ptr).get_info(result)
    return ret, result

def get_activated_protocol_features(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_activated_protocol_features(params, result)
    return ret, result

def get_block(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_block(params, result)
    return ret, result

def get_block_header_state(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_block_header_state(params, result)
    return ret, result

def get_account(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_account(params, result)
    return ret, result

def get_code(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_code(params, result)
    return ret, result

def get_code_hash(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_code_hash(params, result)
    return ret, result

def get_abi(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_abi(params, result)
    return ret, result

def get_raw_code_and_abi(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_raw_code_and_abi(params, result)
    return ret, result

def get_raw_abi(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_raw_abi(params, result)
    return ret, result

def get_table_rows(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_table_rows(params, result)
    return ret, result

def get_table_by_scope(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_table_by_scope(params, result)
    return ret, result

def get_currency_balance(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_currency_balance(params, result)
    return ret, result

def get_currency_stats(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_currency_stats(params, result)
    return ret, result

def get_producers(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_producers(params, result)
    return ret, result

def get_producer_schedule(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_producer_schedule(params, result)
    return ret, result

def get_scheduled_transactions(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_scheduled_transactions(params, result)
    return ret, result

def abi_json_to_bin(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).abi_json_to_bin(params, result)
    return ret, result

def abi_bin_to_json(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).abi_bin_to_json(params, result)
    return ret, result

def get_required_keys(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_required_keys(params, result)
    return ret, result

def get_transaction_id(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_transaction_id(params, result)
    return ret, result

def get_kv_table_rows(uint64_t ptr, string& params):
    cdef string result
    ret = chain_api(ptr).get_kv_table_rows(params, result)
    return ret, result
