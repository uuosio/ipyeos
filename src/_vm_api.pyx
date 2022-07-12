# cython: c_string_type=str, c_string_encoding=utf8

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool
from libc.stdlib cimport malloc, free


cdef extern from * :
    ctypedef long long int64_t
    ctypedef unsigned long long uint64_t
    ctypedef unsigned int uint32_t
    ctypedef int int32_t
    ctypedef unsigned short uint16_t
    ctypedef unsigned char uint8_t
    ctypedef int __uint128_t

cdef extern from "<Python.h>":
    ctypedef long long PyLongObject

    object PyBytes_FromStringAndSize(const char* str, int size)
    int _PyLong_AsByteArray(PyLongObject* v, unsigned char* bytes, size_t n, int little_endian, int is_signed)

cdef extern from "<uuos.hpp>":
    ctypedef struct vm_api_proxy:
        void prints( const char* cstr )
        void printi( int64_t value )
        void printui( uint64_t value )

        uint32_t read_action_data( void* msg, uint32_t len )
        void send_inline(char *serialized_action, uint32_t size)
        void  eosio_assert( uint32_t test, const char* msg )

        int32_t db_store_i64(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id,  const void* data, uint32_t len);
        void db_update_i64(int32_t iterator, uint64_t payer, const void* data, uint32_t len);
        void db_remove_i64(int32_t iterator);
        int32_t db_get_i64(int32_t iterator, void* data, uint32_t len);
        int32_t db_next_i64(int32_t iterator, uint64_t* primary);
        int32_t db_previous_i64(int32_t iterator, uint64_t* primary);
        int32_t db_find_i64(uint64_t code, uint64_t scope, uint64_t table, uint64_t id);
        int32_t db_lowerbound_i64(uint64_t code, uint64_t scope, uint64_t table, uint64_t id);
        int32_t db_upperbound_i64(uint64_t code, uint64_t scope, uint64_t table, uint64_t id);
        int32_t db_end_i64(uint64_t code, uint64_t scope, uint64_t table);


    vm_api_proxy *get_vm_api_proxy();

apply_callback = None
def apply(a: int, b: int, c: int):
    global apply_callback
    if apply_callback:
        return apply_callback(a, b, c)

def set_apply_callback(fn):
    global apply_callback
    apply_callback = fn

cdef extern void native_apply(uint64_t a, uint64_t b, uint64_t c):
    try:
        apply(a, b, c)
    except Exception as e:
        import traceback
        traceback.print_exc()
        get_vm_api_proxy().eosio_assert(0, str(e))


def prints(const char* cstr):
    get_vm_api_proxy().prints(cstr)

def printi(int64_t value):
    get_vm_api_proxy().printi(value)

def printui(uint64_t value):
    get_vm_api_proxy().printui(value)

def read_action_data(uint32_t length):
    if length == 0:
        data_size = get_vm_api_proxy().read_action_data(<void *>0, 0)
        return data_size, None
    else:
        data = <char *>malloc(length)
        length = get_vm_api_proxy().read_action_data(<void *>data, length)
        ret = length, PyBytes_FromStringAndSize(data, length)
        free(data)
        return ret

def send_inline(serialized_data: bytes):
    print('_vm_api.send_inline:', serialized_data)
    get_vm_api_proxy().send_inline(serialized_data, len(serialized_data))
    print('_vm_api.send_inline end')

def db_store_i64(scope: uint64_t, table: uint64_t, payer: uint64_t, id: uint64_t,  data: bytes):
    return get_vm_api_proxy().db_store_i64(scope, table, payer, id,  <void *><const unsigned char *>data, len(data))

def db_update_i64(iterator: int32_t, payer: uint64_t, data: bytes):
    get_vm_api_proxy().db_update_i64(iterator, payer, <void *><const char *>data, len(data))

def db_remove_i64(iterator: int32_t):
    get_vm_api_proxy().db_remove_i64(iterator)

def db_get_i64(iterator: int32_t, length: int32_t):
    cdef char *buffer
    if length == 0:
        data_size = get_vm_api_proxy().db_get_i64(iterator, <void*>0, 0)
        return data_size, None
    else:
        buffer = <char *>malloc(length)
        data_size = get_vm_api_proxy().db_get_i64(iterator, <void*>buffer, length)
        ret = data_size, PyBytes_FromStringAndSize(buffer, data_size)
        free(buffer)
        return ret

def db_next_i64(iterator: int32_t):
    cdef uint64_t primary = 0
    it = get_vm_api_proxy().db_next_i64(iterator, &primary)
    return it, primary

def db_previous_i64(iterator: int32_t):
    cdef uint64_t primary = 0
    it = get_vm_api_proxy().db_previous_i64(iterator, &primary)
    return it, primary

def db_find_i64(code: uint64_t, scope: uint64_t, table: uint64_t, id: uint64_t):
    return get_vm_api_proxy().db_find_i64(code, scope, table, id)

def db_lowerbound_i64(code: uint64_t, scope: uint64_t, table: uint64_t, id: uint64_t):
    return get_vm_api_proxy().db_lowerbound_i64(code, scope, table, id)

def db_upperbound_i64(code: uint64_t, scope: uint64_t, table: uint64_t, id: uint64_t):
    return get_vm_api_proxy().db_upperbound_i64(code, scope, table, id)

def db_end_i64(code: uint64_t, scope: uint64_t, table: uint64_t):
    return get_vm_api_proxy().db_end_i64(code, scope, table)

