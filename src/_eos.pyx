# cython: c_string_type=str, c_string_encoding=ascii

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

    ctypedef struct uuos_proxy:
        void set_log_level(string& logger_name, int level)
        void set_block_interval_ms(int ms)

        string& get_last_error()
        void set_last_error(string& error)

        void pack_abi(string& msg, vector[char]& packed_message)

        void pack_native_object(int type, string& msg, vector[char]& packed_message)
        void unpack_native_object(int type, string& packed_message, string& msg)

        uint64_t s2n(string& s)
        string n2s(uint64_t n)

        bool set_native_contract(uint64_t contract, const string& native_contract_lib);
        string get_native_contract(uint64_t contract);
        void enable_native_contracts(bool debug);
        bool is_native_contracts_enabled();

        int eos_init(int argc, char** argv);
        int eos_exec();

    uuos_proxy *get_uuos_proxy()

uuosext_init()

def set_log_level(string& logger_name, int level):
    get_uuos_proxy().set_log_level(logger_name, level)

def set_block_interval_ms(int ms):
    get_uuos_proxy().set_block_interval_ms(ms)

def get_last_error():
    return get_uuos_proxy().get_last_error()

def set_last_error(string& error):
    get_uuos_proxy().set_last_error(error)

def pack_abi(string& abi):
    cdef vector[char] packed_abi
    get_uuos_proxy().pack_abi(abi, packed_abi)
    return PyBytes_FromStringAndSize(packed_abi.data(), packed_abi.size())

def pack_native_object(int _type, string& msg):
    cdef vector[char] result
    get_uuos_proxy().pack_native_object(_type, msg, result)
    return PyBytes_FromStringAndSize(result.data(), result.size())

def unpack_native_object(int _type, string& packed_message):
    cdef string result
    get_uuos_proxy().unpack_native_object(_type, packed_message, result)
    return result

def s2n(string& s):
    return get_uuos_proxy().s2n(s)

def n2s(uint64_t n):
    return get_uuos_proxy().n2s(n)

def set_native_contract(uint64_t contract, const string& native_contract_lib):
    return get_uuos_proxy().set_native_contract(contract, native_contract_lib)

def get_native_contract(uint64_t contract):
    return get_uuos_proxy().get_native_contract(contract)

def enable_native_contracts(bool debug):
    get_uuos_proxy().enable_native_contracts(debug)

def is_native_contracts_enabled():
    return get_uuos_proxy().is_native_contracts_enabled()

def init(args):
    cdef int argc;
    cdef char **argv

    argc = len(args)
    argv = <char **>malloc(argc * sizeof(char *))
    for i in range(argc):
        argv[i] = args[i]

    return get_uuos_proxy().eos_init(argc, argv)

def exec():
    return get_uuos_proxy().eos_exec()
