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
    ctypedef unsigned int uint32_t
    ctypedef unsigned short uint16_t
    ctypedef unsigned char uint8_t
    ctypedef int __uint128_t

cdef extern from "<Python.h>":
    ctypedef long long PyLongObject

    object PyBytes_FromStringAndSize(const char* str, int size)
    int _PyLong_AsByteArray(PyLongObject* v, unsigned char* bytes, size_t n, int little_endian, int is_signed)

cdef extern from "_ipyeos.hpp":
    void uuosext_init()

    ctypedef struct ipyeos_proxy:
        void set_log_level(string& logger_name, int level)

        string& get_last_error()
        void set_last_error(string& error)

        void pack_abi(string& msg, vector[char]& packed_message)

        void pack_native_object(int type, string& msg, vector[char]& packed_message)
        void unpack_native_object(int type, string& packed_message, string& msg)

        uint64_t s2n(string& s)
        string n2s(uint64_t n)

        string get_native_contract(uint64_t contract);

        void enable_native_contracts(bool debug);
        bool is_native_contracts_enabled();

        void enable_debug(bool debug);
        bool is_debug_enabled();

        string create_key(string& key_type);
        string get_public_key(string &priv_key);

        string sign_digest(string &priv_key, string &digest);

        int eos_init(int argc, char** argv);
        int eos_exec(int argc, char** argv)

    ipyeos_proxy *get_ipyeos_proxy()

uuosext_init()

def set_log_level(string& logger_name, int level):
    get_ipyeos_proxy().set_log_level(logger_name, level)

def get_last_error():
    ret = get_ipyeos_proxy().get_last_error()
    return ret

def set_last_error(err: str):
    get_ipyeos_proxy().set_last_error(err)

def pack_abi(string& abi):
    cdef vector[char] packed_abi
    get_ipyeos_proxy().pack_abi(abi, packed_abi)
    return PyBytes_FromStringAndSize(packed_abi.data(), packed_abi.size())

def pack_native_object(int _type, string& msg):
    cdef vector[char] result
    get_ipyeos_proxy().pack_native_object(_type, msg, result)
    return PyBytes_FromStringAndSize(result.data(), result.size())

def unpack_native_object(int _type, string& packed_message):
    cdef string result
    get_ipyeos_proxy().unpack_native_object(_type, packed_message, result)
    return result

def s2n(string& s):
    return get_ipyeos_proxy().s2n(s)

def n2s(uint64_t n):
    return get_ipyeos_proxy().n2s(n)

def enable_debug(bool debug):
    get_ipyeos_proxy().enable_debug(debug)

def is_debug_enabled():
    return get_ipyeos_proxy().is_debug_enabled()

def create_key(key_type: str):
    return get_ipyeos_proxy().create_key(key_type)

def get_public_key(priv_key: str):
    return get_ipyeos_proxy().get_public_key(priv_key)

def sign_digest(digest: str, priv_key) -> str:
    return get_ipyeos_proxy().sign_digest(digest, priv_key)

def init(args):
    cdef int argc;
    cdef char **argv

    argc = len(args)
    argv = <char **>malloc(argc * sizeof(char *))
    for i in range(argc):
        argv[i] = args[i]

    return get_ipyeos_proxy().eos_init(argc, argv)

def start(args):
    cdef int argc;
    cdef char **argv

    argc = len(args)
    argv = <char **>malloc(argc * sizeof(char *))
    for i in range(argc):
        argv[i] = args[i]

    return get_ipyeos_proxy().eos_exec(argc, argv)
