# cython: c_string_type=str, c_string_encoding=utf8

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy, memset


cdef extern from * :
    ctypedef long long int64_t
    ctypedef unsigned long long uint64_t
    ctypedef unsigned int uint32_t
    ctypedef int int32_t
    ctypedef unsigned short uint16_t
    ctypedef unsigned char uint8_t
    ctypedef int __uint128_t
    ctypedef unsigned int uint128_t #fake definition
    ctypedef int int128_t #fake definition

    ctypedef char capi_checksum256
    ctypedef char capi_checksum160
    ctypedef char capi_checksum512

cdef extern from "<Python.h>":
    ctypedef long long PyLongObject

    object PyBytes_FromStringAndSize(const char* str, int size)
    int _PyLong_AsByteArray(PyLongObject* v, unsigned char* bytes, size_t n, int little_endian, int is_signed)

cdef extern from "<uuos.hpp>":
    ctypedef struct vm_api_proxy:
        void prints( const char* cstr );
        void prints_l( const char* cstr, uint32_t len);
        void printi( int64_t value );
        void printui( uint64_t value );
        void printi128( const int128_t* value );
        void printui128( const uint128_t* value );
        void printsf(float value);
        void printdf(double value);
        void printqf(const long double* value);
        void printn( uint64_t name );
        void printhex( const void* data, uint32_t datalen );

        uint32_t read_action_data( void* msg, uint32_t len )
        uint32_t action_data_size();


        void  eosio_assert( uint32_t test, const char* msg );
        void  eosio_assert_message( uint32_t test, const char* msg, uint32_t msg_len );
        void  eosio_assert_code( uint32_t test, uint64_t code );
        void eosio_exit( int32_t code );
        uint64_t  current_time();
        bool is_feature_activated( const capi_checksum256* feature_digest );
        uint64_t get_sender();

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

        void require_recipient( uint64_t name );
        void require_auth( uint64_t name );
        bool has_auth( uint64_t name );
        void require_auth2( uint64_t name, uint64_t permission );
        bool is_account( uint64_t name );
        void send_inline(char *serialized_action, uint32_t size);
        void send_context_free_inline(char *serialized_action, uint32_t size);
        uint64_t  publication_time();
        uint64_t current_receiver();

        void assert_sha256( const char* data, uint32_t length, const capi_checksum256* hash );
        void assert_sha1( const char* data, uint32_t length, const capi_checksum160* hash );
        void assert_sha512( const char* data, uint32_t length, const capi_checksum512* hash );
        void assert_ripemd160( const char* data, uint32_t length, const capi_checksum160* hash );
        void sha256( const char* data, uint32_t length, capi_checksum256* hash );
        void sha1( const char* data, uint32_t length, capi_checksum160* hash );
        void sha512( const char* data, uint32_t length, capi_checksum512* hash );
        void ripemd160( const char* data, uint32_t length, capi_checksum160* hash );
        int32_t recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, char* pub, uint32_t publen );
        void assert_recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, const char* pub, uint32_t publen );

        #transaction.h
        void send_deferred(const uint128_t sender_id, uint64_t payer, const char *serialized_transaction, uint32_t size, uint32_t replace_existing);
        int32_t cancel_deferred(const uint128_t sender_id);
        uint32_t read_transaction(char *buffer, uint32_t size);
        uint32_t transaction_size();
        int32_t tapos_block_num();
        int32_t tapos_block_prefix();
        uint32_t expiration();
        int32_t get_action( uint32_t type, uint32_t index, char* buff, uint32_t size );
        int32_t get_context_free_data( uint32_t index, char* buff, uint32_t size );

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

cdef extern int native_apply(uint64_t a, uint64_t b, uint64_t c):
    try:
        return apply(a, b, c)
    except Exception as e:
        import traceback
        traceback.print_exc()
        api().eosio_assert(0, str(e))

def prints(const char* cstr):
    api().prints(cstr)

#void prints_l( const char* cstr, uint32_t len);
def prints_l(cstr: bytes):
    api().prints_l(cstr, len(cstr))

def printi(int64_t value):
    api().printi(value)

def printui(uint64_t value):
    api().printui(value)

# void printi128( const int128_t* value );
def printi128(value: bytes):
    assert len(value) == 16, "printi128: bad value size"
    api().printi128(<int128_t *><char *>value)

# void printui128( const uint128_t* value );
def printui128(value: bytes):
    assert len(value) == 16, "printui128: bad value size"
    api().printui128(<uint128_t *><char *>value)

# void printsf(float value);
def printsf(value: bytes):
    assert len(value) == 4, "printsf: bad value size"
    api().printsf((<float*><char *>value)[0])

# void printdf(double value);
def printdf(value: bytes):
    api().printdf((<double *><char *>value)[0])

# void printqf(const long double* value);
def printqf(value: bytes):
    api().printqf(<long double *><char *>value)

# void printn( uint64_t name );
def printn( uint64_t name ):
    api().printn(name)

# void printhex( const void* data, uint32_t datalen );
def printhex( data: bytes):
    api().printhex(<void *><char *>data, len(data))


# uint32_t action_data_size();
def action_data_size():
    return api().action_data_size()

def read_action_data():
    cdef uint32_t length = action_data_size()
    data = <char *>malloc(length)
    length = api().read_action_data(<void *>data, length)
    ret = PyBytes_FromStringAndSize(data, length)
    free(data)
    return ret

# void require_recipient( uint64_t name );
def require_recipient(uint64_t name):
    api().require_recipient(name)

# void require_auth( uint64_t name );
def require_auth(uint64_t name):
    api().require_auth(name)

# bool has_auth( uint64_t name );
def has_auth(uint64_t name):
    return api().has_auth(name)

# void require_auth2( uint64_t name, uint64_t permission );
def require_auth2(uint64_t name, uint64_t permission):
    api().require_auth2(name, permission)

# bool is_account( uint64_t name );
def is_account(uint64_t name):
    return api().is_account(name)

def send_inline(serialized_data: bytes):
    api().send_inline(serialized_data, len(serialized_data))

def send_context_free_inline(serialized_data: bytes):
    api().send_inline(serialized_data, len(serialized_data))

# uint64_t  publication_time();
def publication_time():
    return api().publication_time()

# uint64_t current_receiver();
def current_receiver():
    return api().current_receiver()

# void  eosio_assert( uint32_t test, const char* msg );
def eosio_assert(uint32_t test, msg: bytes):
    api().eosio_assert(test, <char *>msg)

# void  eosio_assert_message( uint32_t test, const char* msg, uint32_t msg_len );
def eosio_assert_message(uint32_t test, msg: bytes):
    api().eosio_assert_message(test, <char *>msg, len(msg))

# void  eosio_assert_code( uint32_t test, uint64_t code );
def eosio_assert_code(uint32_t test, uint64_t code):
    api().eosio_assert_code(test, code)

# void eosio_exit( int32_t code );
def eosio_exit( int32_t code ):
    api().eosio_exit(code)

# uint64_t  current_time();
def current_time():
    return api().current_time()

# bool is_feature_activated( const capi_checksum256* feature_digest );
def is_feature_activated(feature_digest: bytes):
    return api().is_feature_activated(<capi_checksum256*><char *>feature_digest)

# uint64_t get_sender();
def get_sender():
    return api().get_sender()


# void assert_sha256( const char* data, uint32_t length, const capi_checksum256* hash );
def assert_sha256(data: bytes, hash: bytes):
    assert len(hash) == 32, "assert_sha256: bad hash size"
    api().assert_sha256(<char *>data, len(data), <capi_checksum256*><char *>hash)

# void assert_sha1( const char* data, uint32_t length, const capi_checksum160* hash );
def assert_sha1(data: bytes, hash: bytes):
    assert len(hash) == 20, "assert_sha1: bad hash size"
    api().assert_sha1(<char *>data, len(data), <capi_checksum160*><char *>hash)

# void assert_sha512( const char* data, uint32_t length, const capi_checksum512* hash );
def assert_sha512(data: bytes, hash: bytes):
    assert len(hash) == 64, "assert_sha512: bad hash size"
    api().assert_sha512(<char *>data, len(data), <capi_checksum512*><char *>hash)

# void assert_ripemd160( const char* data, uint32_t length, const capi_checksum160* hash );
def assert_ripemd160(data: bytes, hash: bytes):
    assert len(hash) == 20, "assert_ripemd160: bad hash size"
    api().assert_ripemd160(<char *>data, len(data), <capi_checksum160*><char *>hash)

# void sha256( const char* data, uint32_t length, capi_checksum256* hash );
def sha256(data: bytes):
    cdef capi_checksum256 h
    api().sha256(<char *>data, len(data), &h)
    return PyBytes_FromStringAndSize(<char *>&h, 32)

# void sha1( const char* data, uint32_t length, capi_checksum160* hash );
def sha1(data: bytes):
    cdef capi_checksum160 h
    api().sha1(<char *>data, len(data), &h)
    return PyBytes_FromStringAndSize(<char *>&h, 20)

# void sha512( const char* data, uint32_t length, capi_checksum512* hash );
def sha512(data: bytes):
    cdef capi_checksum512 h
    api().sha512(<char *>data, len(data), &h)
    return PyBytes_FromStringAndSize(<char *>&h, 64)

# void ripemd160( const char* data, uint32_t length, capi_checksum160* hash );
def ripemd160(data: bytes):
    cdef capi_checksum160 h
    api().ripemd160(<char *>data, len(data), &h)
    return PyBytes_FromStringAndSize(<char *>&h, 20)

# int32_t recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, char* pub, uint32_t publen );
def recover_key(digest: bytes, sig: bytes):
    cdef char pub[34]
    api().recover_key(<capi_checksum256*><char *>digest, <char *>sig, len(sig), pub, 34)
    return PyBytes_FromStringAndSize(pub, 34)

# void assert_recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, const char* pub, uint32_t publen );
def assert_recover_key(digest: bytes, sig: bytes, pub: bytes):
    assert len(pub) == 34, "assert_recover_key: bad pub size"
    api().assert_recover_key(<capi_checksum256*><char *>digest, <char *>sig, len(sig), <char *>pub, 34)

#transaction.h
# void send_deferred(const uint128_t sender_id, uint64_t payer, const char *serialized_transaction, uint32_t size, uint32_t replace_existing = 0);
def send_deferred(sender_id: bytes, uint64_t payer, serialized_transaction: bytes, uint32_t replace_existing):
    cdef uint128_t _sender_id = 0
    assert len(sender_id) == 16, "send_defered: bad sender_id size"
    memcpy(&_sender_id, <char *>sender_id, 16)
    api().send_deferred(_sender_id, payer, <char *>serialized_transaction, len(serialized_transaction), replace_existing)

# int32_t cancel_deferred(const uint128_t sender_id);
def cancel_deferred(sender_id: bytes):
    cdef uint128_t _sender_id
    assert len(sender_id) == 16, "send_defered: bad sender_id size"
    memcpy(&_sender_id, <char *>sender_id, 16)
    api().cancel_deferred(_sender_id)

# uint32_t read_transaction(char *buffer, uint32_t size);
def read_transaction():
    size = transaction_size()
    buffer = <char *>malloc(size)
    api().read_transaction(buffer, size)
    ret = PyBytes_FromStringAndSize(buffer, size)
    free(buffer)
    return ret

# uint32_t transaction_size();
def transaction_size():
    return api().transaction_size() 

# int32_t tapos_block_num();
def tapos_block_num():
    return api().tapos_block_num()

# int32_t tapos_block_prefix();
def tapos_block_prefix():
    return api().tapos_block_prefix()

# uint32_t expiration();
def expiration():
    return api().expiration()

# int32_t get_action( uint32_t type, uint32_t index, char* buff, uint32_t size );
def get_action( uint32_t _type, uint32_t index):
    size = api().get_action(_type, index, <char *>0, 0)
    if size == 0:
        return None
    buff = <char *>malloc(size)
    api().get_action(_type, index, buff, size)
    ret = PyBytes_FromStringAndSize(buff, size)
    free(buff)
    return ret

# int32_t get_context_free_data( uint32_t index, char* buff, uint32_t size );
def get_context_free_data(uint32_t index):
    size = api().get_context_free_data(index, <char *>0, 0)
    if size == 0:
        return None
    buff = <char *>malloc(size)
    api().get_context_free_data(index, buff, size)
    ret = PyBytes_FromStringAndSize(buff, size)
    free(buff)
    return ret


def db_store_i64(scope: uint64_t, table: uint64_t, payer: uint64_t, id: uint64_t,  data: bytes):
    return api().db_store_i64(scope, table, payer, id,  <void *><const unsigned char *>data, len(data))

def db_update_i64(iterator: int32_t, payer: uint64_t, data: bytes):
    api().db_update_i64(iterator, payer, <void *><const char *>data, len(data))

def db_remove_i64(iterator: int32_t):
    api().db_remove_i64(iterator)

def db_get_i64(iterator: int32_t):
    cdef char *buffer
    buffer_size = api().db_get_i64(iterator, <void*>0, 0)
    buffer = <char *>malloc(buffer_size)
    api().db_get_i64(iterator, <void*>buffer, buffer_size)
    ret = PyBytes_FromStringAndSize(buffer, buffer_size)
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
    return it, int.to_bytes(secondary, 8, 'little')

# int32_t db_idx64_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint64_t* secondary, uint64_t* primary);
def db_idx64_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint64_t secondary):
    cdef uint64_t primary = 0
    it = api().db_idx64_find_secondary(code, scope, table, &secondary, &primary)
    return it, primary

# int32_t db_idx64_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t* secondary, uint64_t* primary);
def db_idx64_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t secondary, uint64_t primary):
    it = api().db_idx64_lowerbound(code, scope, table, &secondary, &primary)
    _secondary = PyBytes_FromStringAndSize(<char *>&secondary, 8)
    return it, _secondary, primary

# int32_t db_idx64_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t* secondary, uint64_t* primary);
def db_idx64_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t secondary, uint64_t primary):
    it = api().db_idx64_upperbound(code, scope, table, &secondary, &primary)
    _secondary = PyBytes_FromStringAndSize(<char *>&secondary, 8)
    return it, _secondary, primary

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
    assert len(secondary) == 16, "db_idx128_find_secondary: bad secondary size: %d"%(len(secondary),)
    memcpy(&_secondary, <char *>secondary, 16)
    it = api().db_idx128_find_secondary(code, scope, table, &_secondary, &primary)
    return it, primary

# int32_t db_idx128_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* secondary, uint64_t* primary);
def db_idx128_lowerbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef uint128_t _secondary = 0
    assert len(secondary) == 16, "db_idx128_lowerbound: bad secondary size: %d"%(len(secondary),)
    memcpy(&_secondary, <char *>secondary, 16)
    it = api().db_idx128_lowerbound(code, scope, table, &_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 16), primary

# int32_t db_idx128_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* secondary, uint64_t* primary);
def db_idx128_upperbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef uint128_t _secondary = 0
    assert len(secondary) == 16, "db_idx128_upperbound: bad secondary size: %d"%(len(secondary),)
    memcpy(&_secondary, <char *>secondary, 16)
    it = api().db_idx128_upperbound(code, scope, table, &_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 16), primary

# int32_t db_idx128_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx128_end(uint64_t code, uint64_t scope, uint64_t table):
    return api().db_idx128_end(code, scope, table)

# int32_t db_idx256_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const uint128_t* data, uint32_t data_len );
def db_idx256_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, data: bytes):
    assert len(data) == 32, "db_idx256_store: bad data size: %d"%(len(data),)
    return api().db_idx256_store(scope, table, payer, id, <uint128_t *><char *>data, 2)

# void db_idx256_update(int32_t iterator, uint64_t payer, const uint128_t* data, uint32_t data_len);
def db_idx256_update(int32_t iterator, uint64_t payer, data: bytes):
    assert len(data) == 32, "db_idx256_update: bad data size: %d"%(len(data),)
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
    memset(data, 0, 32)
    it = api().db_idx256_find_primary(code, scope, table, data, 2, primary)
    return it, PyBytes_FromStringAndSize(<char *>data, 32)

# int32_t db_idx256_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint128_t* data, uint32_t data_len, uint64_t* primary);
def db_idx256_find_secondary(uint64_t code, uint64_t scope, uint64_t table, data: bytes):
    cdef uint64_t primary = 0
    assert len(data) == 32, "db_idx256_find_secondary: bad data size: %d"%(len(data),)
    it = api().db_idx256_find_secondary(code, scope, table, <uint128_t*><char *>data, 2, &primary)
    return it, primary

# int32_t db_idx256_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* data, uint32_t data_len, uint64_t* primary);
def db_idx256_lowerbound(uint64_t code, uint64_t scope, uint64_t table, data: bytes, uint64_t primary):
    cdef uint128_t _data[2]
    assert len(data) == 32, "db_idx256_lowerbound: bad data size: %d"%(len(data),)
    memcpy(_data, <char *>data, 32)
    it = api().db_idx256_lowerbound(code, scope, table, _data, 2, &primary)
    return it, PyBytes_FromStringAndSize(<char *>_data, 32), primary

# int32_t db_idx256_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* data, uint32_t data_len, uint64_t* primary);
def db_idx256_upperbound(uint64_t code, uint64_t scope, uint64_t table, data: bytes, uint64_t primary):
    cdef uint128_t _data[2]
    assert len(data) == 32, "db_idx256_upperbound: bad data size: %d"%(len(data),)
    memcpy(_data, <char *>data, 32)
    it = api().db_idx256_upperbound(code, scope, table, _data, 2, &primary)
    return it, PyBytes_FromStringAndSize(<char *>_data, 32), primary

# int32_t db_idx256_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx256_end(uint64_t code, uint64_t scope, uint64_t table):
    return api().db_idx256_end(code, scope, table)

# int32_t db_idx_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const double* secondary);
def db_idx_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, secondary: bytes):
    assert len(secondary) == 8, "db_idx_double_store: bad data size: %d"%(len(secondary),)
    return api().db_idx_double_store(scope, table, payer, id, <double*><char *>secondary)

# void db_idx_double_update(int32_t iterator, uint64_t payer, const double* secondary);
def db_idx_double_update(int32_t iterator, uint64_t payer, secondary: bytes):
    assert len(secondary) == 8, "db_idx_double_update: bad data size: %d"%(len(secondary),)
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
    it = api().db_idx_long_double_previous(iterator, &primary)
    return it, primary

# int32_t db_idx_long_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, long double* secondary, uint64_t primary);
def db_idx_long_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t primary):
    cdef long double secondary = 0.0
    it = api().db_idx_long_double_find_primary(code, scope, table, &secondary, primary)
    return it, PyBytes_FromStringAndSize(<char *>&secondary, 16)

# int32_t db_idx_long_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const long double* secondary, uint64_t* primary);
def db_idx_long_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes):
    cdef uint64_t primary = 0
    assert len(secondary) == 16, "db_idx_long_double_find_secondary: bad data size: %d"%(len(secondary),)
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
