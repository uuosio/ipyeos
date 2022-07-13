# cython: c_string_type=str, c_string_encoding=utf8

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy


cdef extern from * :
    ctypedef long long int64_t
    ctypedef unsigned long long uint64_t
    ctypedef unsigned int uint32_t
    ctypedef int int32_t
    ctypedef unsigned short uint16_t
    ctypedef unsigned char uint8_t
    ctypedef int __uint128_t
    ctypedef unsigned int uint128_t

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
        uint32_t action_data_size();

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

        int32_t db_idx64_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const uint64_t* secondary);
        void db_idx64_update(int32_t iterator, uint64_t payer, const uint64_t* secondary);
        void db_idx64_remove(int32_t iterator);
        int32_t db_idx64_next(int32_t iterator, uint64_t* primary);
        int32_t db_idx64_previous(int32_t iterator, uint64_t* primary);
        int32_t db_idx64_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t* secondary, uint64_t primary);
        int32_t db_idx64_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint64_t* secondary, uint64_t* primary);
        int32_t db_idx64_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t* secondary, uint64_t* primary);
        int32_t db_idx64_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t* secondary, uint64_t* primary);
        int32_t db_idx64_end(uint64_t code, uint64_t scope, uint64_t table);
        int32_t db_idx128_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const uint128_t* secondary);
        void db_idx128_update(int32_t iterator, uint64_t payer, const uint128_t* secondary);
        void db_idx128_remove(int32_t iterator);
        int32_t db_idx128_next(int32_t iterator, uint64_t* primary);
        int32_t db_idx128_previous(int32_t iterator, uint64_t* primary);
        int32_t db_idx128_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint128_t* secondary, uint64_t primary);
        int32_t db_idx128_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint128_t* secondary, uint64_t* primary);
        int32_t db_idx128_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* secondary, uint64_t* primary);
        int32_t db_idx128_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* secondary, uint64_t* primary);
        int32_t db_idx128_end(uint64_t code, uint64_t scope, uint64_t table);
        int32_t db_idx256_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const uint128_t* data, uint32_t data_len );
        void db_idx256_update(int32_t iterator, uint64_t payer, const uint128_t* data, uint32_t data_len);
        void db_idx256_remove(int32_t iterator);
        int32_t db_idx256_next(int32_t iterator, uint64_t* primary);
        int32_t db_idx256_previous(int32_t iterator, uint64_t* primary);
        int32_t db_idx256_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint128_t* data, uint32_t data_len, uint64_t primary);
        int32_t db_idx256_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint128_t* data, uint32_t data_len, uint64_t* primary);
        int32_t db_idx256_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* data, uint32_t data_len, uint64_t* primary);
        int32_t db_idx256_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* data, uint32_t data_len, uint64_t* primary);
        int32_t db_idx256_end(uint64_t code, uint64_t scope, uint64_t table);
        int32_t db_idx_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const double* secondary);
        void db_idx_double_update(int32_t iterator, uint64_t payer, const double* secondary);
        void db_idx_double_remove(int32_t iterator);
        int32_t db_idx_double_next(int32_t iterator, uint64_t* primary);
        int32_t db_idx_double_previous(int32_t iterator, uint64_t* primary);
        int32_t db_idx_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, double* secondary, uint64_t primary);
        int32_t db_idx_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const double* secondary, uint64_t* primary);
        int32_t db_idx_double_lowerbound(uint64_t code, uint64_t scope, uint64_t table, double* secondary, uint64_t* primary);
        int32_t db_idx_double_upperbound(uint64_t code, uint64_t scope, uint64_t table, double* secondary, uint64_t* primary);
        int32_t db_idx_double_end(uint64_t code, uint64_t scope, uint64_t table);
        int32_t db_idx_long_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const long double* secondary);
        void db_idx_long_double_update(int32_t iterator, uint64_t payer, const long double* secondary);
        void db_idx_long_double_remove(int32_t iterator);
        int32_t db_idx_long_double_next(int32_t iterator, uint64_t* primary);
        int32_t db_idx_long_double_previous(int32_t iterator, uint64_t* primary);
        int32_t db_idx_long_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, long double* secondary, uint64_t primary);
        int32_t db_idx_long_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const long double* secondary, uint64_t* primary);
        int32_t db_idx_long_double_lowerbound(uint64_t code, uint64_t scope, uint64_t table, long double* secondary, uint64_t* primary);
        int32_t db_idx_long_double_upperbound(uint64_t code, uint64_t scope, uint64_t table, long double* secondary, uint64_t* primary);
        int32_t db_idx_long_double_end(uint64_t code, uint64_t scope, uint64_t table);

    vm_api_proxy *get_vm_api_proxy();

cdef vm_api_proxy* api():
    return get_vm_api_proxy()

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
        api().eosio_assert(0, str(e))


def prints(const char* cstr):
    api().prints(cstr)

def printi(int64_t value):
    api().printi(value)

def printui(uint64_t value):
    api().printui(value)

# uint32_t action_data_size();
def action_data_size():
    return api().action_data_size()

def read_action_data(uint32_t length):
    if length == 0:
        data_size = api().read_action_data(<void *>0, 0)
        return data_size, None
    else:
        data = <char *>malloc(length)
        length = api().read_action_data(<void *>data, length)
        ret = length, PyBytes_FromStringAndSize(data, length)
        free(data)
        return ret

def send_inline(serialized_data: bytes):
    print('_vm_api.send_inline:', serialized_data)
    api().send_inline(serialized_data, len(serialized_data))
    print('_vm_api.send_inline end')

def db_store_i64(scope: uint64_t, table: uint64_t, payer: uint64_t, id: uint64_t,  data: bytes):
    return api().db_store_i64(scope, table, payer, id,  <void *><const unsigned char *>data, len(data))

def db_update_i64(iterator: int32_t, payer: uint64_t, data: bytes):
    api().db_update_i64(iterator, payer, <void *><const char *>data, len(data))

def db_remove_i64(iterator: int32_t):
    api().db_remove_i64(iterator)

def db_get_i64(iterator: int32_t, length: int32_t):
    cdef char *buffer
    if length == 0:
        data_size = api().db_get_i64(iterator, <void*>0, 0)
        return data_size, None
    else:
        buffer = <char *>malloc(length)
        data_size = api().db_get_i64(iterator, <void*>buffer, length)
        ret = data_size, PyBytes_FromStringAndSize(buffer, data_size)
        free(buffer)
        return ret

def db_next_i64(iterator: int32_t):
    cdef uint64_t primary = 0
    it = api().db_next_i64(iterator, &primary)
    return it, primary

def db_previous_i64(iterator: int32_t):
    cdef uint64_t primary = 0
    it = api().db_previous_i64(iterator, &primary)
    return it, primary

def db_find_i64(code: uint64_t, scope: uint64_t, table: uint64_t, id: uint64_t):
    return api().db_find_i64(code, scope, table, id)

def db_lowerbound_i64(code: uint64_t, scope: uint64_t, table: uint64_t, id: uint64_t):
    return api().db_lowerbound_i64(code, scope, table, id)

def db_upperbound_i64(code: uint64_t, scope: uint64_t, table: uint64_t, id: uint64_t):
    return api().db_upperbound_i64(code, scope, table, id)

def db_end_i64(code: uint64_t, scope: uint64_t, table: uint64_t):
    return api().db_end_i64(code, scope, table)

# int32_t db_idx64_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const uint64_t* secondary);
def db_idx64_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, uint64_t secondary):
    return api().db_idx64_store(scope, table, payer, id, &secondary)

# void db_idx64_update(int32_t iterator, uint64_t payer, const uint64_t* secondary);
def db_idx64_update(int32_t iterator, uint64_t payer, uint64_t secondary):
    api().db_idx64_update(iterator, payer, &secondary)

# void db_idx64_remove(int32_t iterator);
def db_idx64_remove(int32_t iterator):
    api().db_idx64_remove(iterator)

# int32_t db_idx64_next(int32_t iterator, uint64_t* primary);
def db_idx64_next(int32_t iterator):
    cdef uint64_t primary = 0
    it = api().db_idx64_next(iterator, &primary)
    return it, primary 

# int32_t db_idx64_previous(int32_t iterator, uint64_t* primary);
def db_idx64_previous(int32_t iteratory):
    cdef uint64_t primary = 0
    it = api().db_idx64_previous(iteratory, &primary)
    return it, primary 

# int32_t db_idx64_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t* secondary, uint64_t primary);
def db_idx64_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t primary):
    cdef uint64_t secondary = 0
    it = api().db_idx64_find_primary(code, scope, table, &secondary, primary)
    return it, secondary

# int32_t db_idx64_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint64_t* secondary, uint64_t* primary);
def db_idx64_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint64_t secondary):
    cdef uint64_t primary = 0
    it = api().db_idx64_find_secondary(code, scope, table, &secondary, &primary)
    return it, primary

# int32_t db_idx64_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t* secondary, uint64_t* primary);
def db_idx64_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t secondary, uint64_t primary):
    it = api().db_idx64_lowerbound(code, scope, table, &secondary, &primary)
    return it, secondary, primary

# int32_t db_idx64_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t* secondary, uint64_t* primary);
def db_idx64_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t secondary, uint64_t primary):
    it = api().db_idx64_upperbound(code, scope, table, &secondary, &primary)
    return it, secondary, primary

# int32_t db_idx64_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx64_end(uint64_t code, uint64_t scope, uint64_t table):
    return api().db_idx64_end(code, scope, table)

# int32_t db_idx128_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const uint128_t* secondary);
def db_idx128_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, secondary: bytes):
    assert len(secondary) == 16, "db_idx128_store: bad secondary size"
    return api().db_idx128_store(scope, table, payer, id, <uint128_t*><char *>secondary)

# void db_idx128_update(int32_t iterator, uint64_t payer, const uint128_t* secondary);
def db_idx128_update(int32_t iterator, uint64_t payer, secondary: bytes):
    assert len(secondary) == 16, "db_idx128_update: bad secondary size"
    api().db_idx128_update(iterator, payer, <uint128_t*><char *>secondary)

# void db_idx128_remove(int32_t iterator);
def db_idx128_remove(int32_t iterator):
    api().db_idx128_remove(iterator)

# int32_t db_idx128_next(int32_t iterator, uint64_t* primary);
def db_idx128_next(int32_t iterator):
    cdef uint64_t primary = 0
    it = api().db_idx128_next(iterator, &primary)
    return it, primary

# int32_t db_idx128_previous(int32_t iterator, uint64_t* primary);
def db_idx128_previous(int32_t iterator):
    cdef uint64_t primary = 0
    it = api().db_idx128_previous(iterator, &primary)
    return it, primary

# int32_t db_idx128_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint128_t* secondary, uint64_t primary);
def db_idx128_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t primary):
    cdef uint128_t secondary = 0
    it = api().db_idx128_find_primary(code, scope, table, &secondary, primary)
    return it, PyBytes_FromStringAndSize(<char *>&secondary, 16)

# int32_t db_idx128_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint128_t* secondary, uint64_t* primary);
def db_idx128_find_secondary(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes):
    cdef uint64_t primary = 0
    cdef uint128_t _secondary = 0
    assert len(secondary) == 16, "db_idx128_find_secondary: bad secondary size"
    memcpy(&_secondary, <char *>secondary, 16)
    it = api().db_idx128_find_secondary(code, scope, table, <uint128_t*><char *>_secondary, &primary)
    return it, primary

# int32_t db_idx128_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* secondary, uint64_t* primary);
def db_idx128_lowerbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef uint128_t _secondary = 0
    assert len(secondary) == 16, "db_idx128_lowerbound: bad secondary size"
    memcpy(&_secondary, <char *>secondary, 16)
    it = api().db_idx128_lowerbound(code, scope, table, &_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>_secondary, 16), primary

# int32_t db_idx128_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* secondary, uint64_t* primary);
def db_idx128_upperbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef uint128_t _secondary = 0
    assert len(secondary) == 16, "db_idx128_upperbound: bad secondary size"
    memcpy(&_secondary, <char *>secondary, 16)
    it = api().db_idx128_upperbound(code, scope, table, &_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>_secondary, 16), primary

# int32_t db_idx128_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx128_end(uint64_t code, uint64_t scope, uint64_t table):
    return api().db_idx128_end(code, scope, table)

# int32_t db_idx256_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const uint128_t* data, uint32_t data_len );
def db_idx256_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, data: bytes):
    assert len(data) == 32, "db_idx256_store: bad data size"
    return api().db_idx256_store(scope, table, payer, id, <uint128_t *><char *>data, 2)

# void db_idx256_update(int32_t iterator, uint64_t payer, const uint128_t* data, uint32_t data_len);
def db_idx256_update(int32_t iterator, uint64_t payer, data: bytes):
    assert len(data) == 32, "db_idx256_update: bad data size"
    api().db_idx256_update(iterator, payer, <uint128_t*><char *>data, 2)

# void db_idx256_remove(int32_t iterator);
def db_idx256_remove(int32_t iterator):
    api().db_idx256_remove(iterator)

# int32_t db_idx256_next(int32_t iterator, uint64_t* primary);
def db_idx256_next(int32_t iterator):
    cdef uint64_t primary = 0
    it = api().db_idx256_next(iterator, &primary)
    return it, primary

# int32_t db_idx256_previous(int32_t iterator, uint64_t* primary);
def db_idx256_previous(int32_t iterator):
    cdef uint64_t primary = 0
    it = api().db_idx256_previous(iterator, &primary)
    return it, primary

# int32_t db_idx256_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint128_t* data, uint32_t data_len, uint64_t primary);
def db_idx256_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t primary):
    cdef uint128_t data[2]
    it = api().db_idx256_find_primary(code, scope, table, data, 2, primary)
    return it, primary

# int32_t db_idx256_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint128_t* data, uint32_t data_len, uint64_t* primary);
def db_idx256_find_secondary(uint64_t code, uint64_t scope, uint64_t table, data: bytes):
    cdef uint64_t primary = 0
    assert len(data) == 32, "db_idx256_find_secondary: bad data size"
    it = api().db_idx256_find_secondary(code, scope, table, <uint128_t*><char *>data, 2, &primary)

# int32_t db_idx256_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* data, uint32_t data_len, uint64_t* primary);
def db_idx256_lowerbound(uint64_t code, uint64_t scope, uint64_t table, data: bytes, uint64_t primary):
    assert len(data) == 32, "db_idx256_find_secondary: bad data size"
    it = api().db_idx256_lowerbound(code, scope, table, <uint128_t*><char *>data, 2, &primary)
    return it, data, primary

# int32_t db_idx256_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* data, uint32_t data_len, uint64_t* primary);
def db_idx256_upperbound(uint64_t code, uint64_t scope, uint64_t table, data: bytes, uint64_t primary):
    assert len(data) == 32, "db_idx256_find_secondary: bad data size"
    it = api().db_idx256_upperbound(code, scope, table, <uint128_t*><char *>data, 2, &primary)
    return it, data, primary

# int32_t db_idx256_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx256_end(uint64_t code, uint64_t scope, uint64_t table):
    return api().db_idx256_end(code, scope, table)

# int32_t db_idx_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const double* secondary);
def db_idx_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, secondary: bytes):
    return api().db_idx_double_store(scope, table, payer, id, <double*><char *>secondary)

# void db_idx_double_update(int32_t iterator, uint64_t payer, const double* secondary);
def db_idx_double_update(int32_t iterator, uint64_t payer, secondary: bytes):
    api().db_idx_double_update(iterator, payer, <double*><char*>secondary)

# void db_idx_double_remove(int32_t iterator);
def db_idx_double_remove(int32_t iterator):
    api().db_idx_double_remove(iterator)

# int32_t db_idx_double_next(int32_t iterator, uint64_t* primary);
def db_idx_double_next(int32_t iterator):
    cdef uint64_t primary = 0
    it = api().db_idx_double_next(iterator, &primary)
    return it, primary

# int32_t db_idx_double_previous(int32_t iterator, uint64_t* primary);
def db_idx_double_previous(int32_t iterator):
    cdef uint64_t primary = 0
    it = api().db_idx_double_previous(iterator, &primary)
    return it, primary

# int32_t db_idx_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, double* secondary, uint64_t primary);
def db_idx_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t primary):
    cdef double secondary = 0.0
    it = api().db_idx_double_find_primary(code, scope, table, &secondary, primary)
    return it, PyBytes_FromStringAndSize(<char*>&secondary, 8)

# int32_t db_idx_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const double* secondary, uint64_t* primary);
def db_idx_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes):
    cdef uint64_t primary = 0
    assert len(secondary) == 8, "db_idx_double_find_secondary:bad secondary size"
    it = api().db_idx_double_find_secondary(code, scope, table, <double *><char *>secondary, &primary)
    return it, primary

# int32_t db_idx_double_lowerbound(uint64_t code, uint64_t scope, uint64_t table, double* secondary, uint64_t* primary);
def db_idx_double_lowerbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef double _secondary = 0.0
    assert len(secondary) == 8, "db_idx_double_lowerbound:bad secondary size"
    memcpy(&_secondary, <char *>secondary, 8)
    it = api().db_idx_double_lowerbound(code, scope, table, &_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 8), primary

# int32_t db_idx_double_upperbound(uint64_t code, uint64_t scope, uint64_t table, double* secondary, uint64_t* primary);
def db_idx_double_upperbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef double _secondary = 0.0
    assert len(secondary) == 8, "db_idx_double_upperbound:bad secondary size"
    memcpy(&_secondary, <char *>secondary, 8)
    it = api().db_idx_double_upperbound(code, scope, table, &_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 8), primary

# int32_t db_idx_double_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx_double_end(uint64_t code, uint64_t scope, uint64_t table):
    return api().db_idx_double_end(code, scope, table)

# int32_t db_idx_long_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const long double* secondary);
def db_idx_long_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, secondary: bytes):
    assert len(secondary) == 16, "db_idx_long_double_store:bad secondary size"
    return api().db_idx_long_double_store(scope, table, payer, id, <const long double*><char *>secondary)

# void db_idx_long_double_update(int32_t iterator, uint64_t payer, const long double* secondary);
def db_idx_long_double_update(int32_t iterator, uint64_t payer, secondary: bytes):
    assert len(secondary) == 16, "db_idx_long_double_update:bad secondary size"
    api().db_idx_long_double_update(iterator, payer, <const long double*><char *>secondary)

# void db_idx_long_double_remove(int32_t iterator);
def db_idx_long_double_remove(int32_t iterator):
    api().db_idx_long_double_remove(iterator)

# int32_t db_idx_long_double_next(int32_t iterator, uint64_t* primary);
def db_idx_long_double_next(int32_t iterator):
    cdef uint64_t primary = 0
    it = api().db_idx_long_double_next(iterator, &primary)
    return it, primary

# int32_t db_idx_long_double_previous(int32_t iterator, uint64_t* primary);
def db_idx_long_double_previous(int32_t iterator):
    cdef uint64_t primary = 0
    it = api().db_idx_long_double_next(iterator, &primary)
    return it, primary

# int32_t db_idx_long_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, long double* secondary, uint64_t primary);
def db_idx_long_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t primary):
    cdef long double secondary = 0.0
    it = api().db_idx_long_double_find_primary(code, scope, table, &secondary, primary)
    return it, PyBytes_FromStringAndSize(<char *>&secondary, 16)

# int32_t db_idx_long_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const long double* secondary, uint64_t* primary);
def db_idx_long_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes):
    cdef uint64_t primary = 0
    it = api().db_idx_long_double_find_secondary(code, scope, table, <long double *><char *>secondary, &primary)
    return it, primary

# int32_t db_idx_long_double_lowerbound(uint64_t code, uint64_t scope, uint64_t table, long double* secondary, uint64_t* primary);
def db_idx_long_double_lowerbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef long double _secondary = 0.0
    assert len(secondary) == 16, "db_idx_long_double_lowerbound:bad secondary size"
    memcpy(&_secondary, <char *>secondary, 16)
    it = api().db_idx_long_double_lowerbound(code, scope, table, <long double*>&_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 16), primary

# int32_t db_idx_long_double_upperbound(uint64_t code, uint64_t scope, uint64_t table, long double* secondary, uint64_t* primary);
def db_idx_long_double_upperbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef long double _secondary = 0.0
    assert len(secondary) == 16, "db_idx_long_double_upperbound:bad secondary size"
    memcpy(&_secondary, <char *>secondary, 16)
    it = api().db_idx_long_double_upperbound(code, scope, table, <long double*>&_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 16), primary

# int32_t db_idx_long_double_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx_long_double_end(uint64_t code, uint64_t scope, uint64_t table):
    return api().db_idx_long_double_end(code, scope, table)
