# cython: language_level=3, c_string_type=str, c_string_encoding=utf8
from _ipyeos cimport *

cdef extern from * :
    ctypedef uint64_t capi_name
    ctypedef unsigned int uint128_t #fake definition
    ctypedef int int128_t #fake definition
    ctypedef char capi_checksum256
    ctypedef char capi_checksum160
    ctypedef char capi_checksum512

cdef extern from "_ipyeos.hpp":
    bool has_last_exception()

cdef extern from "_vm_api.hpp":

    uint32_t _get_active_producers( capi_name* producers, uint32_t datalen );
    int32_t _db_store_i64(uint64_t scope, capi_name table, capi_name payer, uint64_t id,  const void* data, uint32_t len);
    void _db_update_i64(int32_t iterator, capi_name payer, const void* data, uint32_t len);
    void _db_remove_i64(int32_t iterator);
    int32_t _db_get_i64(int32_t iterator, const void* data, uint32_t len);
    int32_t _db_next_i64(int32_t iterator, uint64_t* primary);
    int32_t _db_previous_i64(int32_t iterator, uint64_t* primary);
    int32_t _db_find_i64(capi_name code, uint64_t scope, capi_name table, uint64_t id);
    int32_t _db_lowerbound_i64(capi_name code, uint64_t scope, capi_name table, uint64_t id);
    int32_t _db_upperbound_i64(capi_name code, uint64_t scope, capi_name table, uint64_t id);
    int32_t _db_end_i64(capi_name code, uint64_t scope, capi_name table);
    int32_t _db_idx64_store(uint64_t scope, capi_name table, capi_name payer, uint64_t id, const uint64_t* secondary);
    void _db_idx64_update(int32_t iterator, capi_name payer, const uint64_t* secondary);
    void _db_idx64_remove(int32_t iterator);
    int32_t _db_idx64_next(int32_t iterator, uint64_t* primary);
    int32_t _db_idx64_previous(int32_t iterator, uint64_t* primary);
    int32_t _db_idx64_find_primary(capi_name code, uint64_t scope, capi_name table, uint64_t* secondary, uint64_t primary);
    int32_t _db_idx64_find_secondary(capi_name code, uint64_t scope, capi_name table, const uint64_t* secondary, uint64_t* primary);
    int32_t _db_idx64_lowerbound(capi_name code, uint64_t scope, capi_name table, uint64_t* secondary, uint64_t* primary);
    int32_t _db_idx64_upperbound(capi_name code, uint64_t scope, capi_name table, uint64_t* secondary, uint64_t* primary);
    int32_t _db_idx64_end(capi_name code, uint64_t scope, capi_name table);
    int32_t _db_idx128_store(uint64_t scope, capi_name table, capi_name payer, uint64_t id, const uint128_t* secondary);
    void _db_idx128_update(int32_t iterator, capi_name payer, const uint128_t* secondary);
    void _db_idx128_remove(int32_t iterator);
    int32_t _db_idx128_next(int32_t iterator, uint64_t* primary);
    int32_t _db_idx128_previous(int32_t iterator, uint64_t* primary);
    int32_t _db_idx128_find_primary(capi_name code, uint64_t scope, capi_name table, uint128_t* secondary, uint64_t primary);
    int32_t _db_idx128_find_secondary(capi_name code, uint64_t scope, capi_name table, const uint128_t* secondary, uint64_t* primary);
    int32_t _db_idx128_lowerbound(capi_name code, uint64_t scope, capi_name table, uint128_t* secondary, uint64_t* primary);
    int32_t _db_idx128_upperbound(capi_name code, uint64_t scope, capi_name table, uint128_t* secondary, uint64_t* primary);
    int32_t _db_idx128_end(capi_name code, uint64_t scope, capi_name table);
    int32_t _db_idx256_store(uint64_t scope, capi_name table, capi_name payer, uint64_t id, const uint128_t* data, uint32_t data_len );
    void _db_idx256_update(int32_t iterator, capi_name payer, const uint128_t* data, uint32_t data_len);
    void _db_idx256_remove(int32_t iterator);
    int32_t _db_idx256_next(int32_t iterator, uint64_t* primary);
    int32_t _db_idx256_previous(int32_t iterator, uint64_t* primary);
    int32_t _db_idx256_find_primary(capi_name code, uint64_t scope, capi_name table, uint128_t* data, uint32_t data_len, uint64_t primary);
    int32_t _db_idx256_find_secondary(capi_name code, uint64_t scope, capi_name table, const uint128_t* data, uint32_t data_len, uint64_t* primary);
    int32_t _db_idx256_lowerbound(capi_name code, uint64_t scope, capi_name table, uint128_t* data, uint32_t data_len, uint64_t* primary);
    int32_t _db_idx256_upperbound(capi_name code, uint64_t scope, capi_name table, uint128_t* data, uint32_t data_len, uint64_t* primary);
    int32_t _db_idx256_end(capi_name code, uint64_t scope, capi_name table);
    int32_t _db_idx_double_store(uint64_t scope, capi_name table, capi_name payer, uint64_t id, const double* secondary);
    void _db_idx_double_update(int32_t iterator, capi_name payer, const double* secondary);
    void _db_idx_double_remove(int32_t iterator);
    int32_t _db_idx_double_next(int32_t iterator, uint64_t* primary);
    int32_t _db_idx_double_previous(int32_t iterator, uint64_t* primary);
    int32_t _db_idx_double_find_primary(capi_name code, uint64_t scope, capi_name table, double* secondary, uint64_t primary);
    int32_t _db_idx_double_find_secondary(capi_name code, uint64_t scope, capi_name table, const double* secondary, uint64_t* primary);
    int32_t _db_idx_double_lowerbound(capi_name code, uint64_t scope, capi_name table, double* secondary, uint64_t* primary);
    int32_t _db_idx_double_upperbound(capi_name code, uint64_t scope, capi_name table, double* secondary, uint64_t* primary);
    int32_t _db_idx_double_end(capi_name code, uint64_t scope, capi_name table);
    int32_t _db_idx_long_double_store(uint64_t scope, capi_name table, capi_name payer, uint64_t id, const long double* secondary);
    void _db_idx_long_double_update(int32_t iterator, capi_name payer, const long double* secondary);
    void _db_idx_long_double_remove(int32_t iterator);
    int32_t _db_idx_long_double_next(int32_t iterator, uint64_t* primary);
    int32_t _db_idx_long_double_previous(int32_t iterator, uint64_t* primary);
    int32_t _db_idx_long_double_find_primary(capi_name code, uint64_t scope, capi_name table, long double* secondary, uint64_t primary);
    int32_t _db_idx_long_double_find_secondary(capi_name code, uint64_t scope, capi_name table, const long double* secondary, uint64_t* primary);
    int32_t _db_idx_long_double_lowerbound(capi_name code, uint64_t scope, capi_name table, long double* secondary, uint64_t* primary);
    int32_t _db_idx_long_double_upperbound(capi_name code, uint64_t scope, capi_name table, long double* secondary, uint64_t* primary);
    int32_t _db_idx_long_double_end(capi_name code, uint64_t scope, capi_name table);
    int32_t _check_transaction_authorization( const char* trx_data,     uint32_t trx_size, const char* pubkeys_data, uint32_t pubkeys_size,const char* perms_data,   uint32_t perms_size);
    int32_t _check_permission_authorization( capi_name account, capi_name permission, const char* pubkeys_data, uint32_t pubkeys_size, const char* perms_data,   uint32_t perms_size, uint64_t delay_us);
    int64_t _get_permission_last_used( capi_name account, capi_name permission );
    int64_t _get_account_creation_time( capi_name account );
    void _assert_sha256( const char* data, uint32_t length, const capi_checksum256* hash );
    void _assert_sha1( const char* data, uint32_t length, const capi_checksum160* hash );
    void _assert_sha512( const char* data, uint32_t length, const capi_checksum512* hash );
    void _assert_ripemd160( const char* data, uint32_t length, const capi_checksum160* hash );
    void _sha256( const char* data, uint32_t length, capi_checksum256* hash );
    void _sha1( const char* data, uint32_t length, capi_checksum160* hash );
    void _sha512( const char* data, uint32_t length, capi_checksum512* hash );
    void _ripemd160( const char* data, uint32_t length, capi_checksum160* hash );
    int _recover_key( const capi_checksum256* digest, const char* sig, size_t siglen, char* pub, size_t publen );
    void _assert_recover_key( const capi_checksum256* digest, const char* sig, size_t siglen, const char* pub, size_t publen );
    uint32_t _read_action_data( void* msg, uint32_t len );
    uint32_t _action_data_size();
    void _require_recipient( capi_name name );
    void _require_auth( capi_name name );
    bool _has_auth( capi_name name );
    void _require_auth2( capi_name name, capi_name permission );
    bool _is_account( capi_name name );
    void _send_inline(char *serialized_action, size_t size);
    void _send_context_free_inline(char *serialized_action, size_t size);
    uint64_t _publication_time();
    capi_name _current_receiver();
    void _prints( const char* cstr );
    void _prints_l( const char* cstr, uint32_t len);
    void _printi( int64_t value );
    void _printui( uint64_t value );
    void _printi128( const int128_t* value );
    void _printui128( const uint128_t* value );
    void _printsf(float value);
    void _printdf(double value);
    void _printqf(const long double* value);
    void _printn( uint64_t name );
    void _printhex( const void* data, uint32_t datalen );
    void _eosio_assert( uint32_t test, const char* msg );
    void _eosio_assert_message( uint32_t test, const char* msg, uint32_t msg_len );
    void _eosio_assert_code( uint32_t test, uint64_t code );
    uint64_t _current_time();
    bool _is_feature_activated( const capi_checksum256* feature_digest );
    capi_name _get_sender();
    void _get_resource_limits( capi_name account, int64_t* ram_bytes, int64_t* net_weight, int64_t* cpu_weight );
    void _set_resource_limits( capi_name account, int64_t ram_bytes, int64_t net_weight, int64_t cpu_weight );
    int64_t _set_proposed_producers( char *producer_data, uint32_t producer_data_size );
    int64_t _set_proposed_producers_ex( uint64_t producer_data_format, char *producer_data, uint32_t producer_data_size );
    bool _is_privileged( capi_name account );
    void _set_privileged( capi_name account, bool is_priv );
    void _set_blockchain_parameters_packed( char* data, uint32_t datalen );
    uint32_t _get_blockchain_parameters_packed( char* data, uint32_t datalen );
    void _preactivate_feature( const capi_checksum256* feature_digest );
    void _send_deferred(const uint128_t& sender_id, capi_name payer, const char *serialized_transaction, size_t size, uint32_t replace_existing);
    int _cancel_deferred(const uint128_t& sender_id);
    size_t _read_transaction(char *buffer, size_t size);
    size_t _transaction_size();
    int _tapos_block_num();
    int _tapos_block_prefix();
    uint32_t _expiration();
    int _get_action( uint32_t type, uint32_t index, char* buff, size_t size );
    int _get_context_free_data( uint32_t index, char* buff, size_t size );
    void _eosio_exit( int32_t code );

    void _set_action_return_value(const char *data, uint32_t data_size);
    uint32_t _get_code_hash(capi_name account, uint32_t struct_version, char* packed_result, uint32_t packed_result_len);
    uint32_t _get_block_num();

    void _sha3( const char* data, uint32_t data_len, char* hash, uint32_t hash_len, int32_t keccak );
    int32_t _blake2_f( uint32_t rounds, const char* state, uint32_t state_len, const char* msg, uint32_t msg_len, 
                    const char* t0_offset, uint32_t t0_len, const char* t1_offset, uint32_t t1_len, int32_t final, char* result, uint32_t result_len);
    int32_t _k1_recover( const char* sig, uint32_t sig_len, const char* dig, uint32_t dig_len, char* pub, uint32_t pub_len);
    int32_t _alt_bn128_add( const char* op1, uint32_t op1_len, const char* op2, uint32_t op2_len, char* result, uint32_t result_len);
    int32_t _alt_bn128_mul( const char* g1, uint32_t g1_len, const char* scalar, uint32_t scalar_len, char* result, uint32_t result_len);
    int32_t _alt_bn128_pair( const char* pairs, uint32_t pairs_len);
    int32_t _mod_exp( const char* base, uint32_t base_len, const char* exp, uint32_t exp_len, const char* mod, uint32_t mod_len, char* result, uint32_t result_len);


def is_cpp_exception_occur():
    return has_last_exception()

apply_callback = None
def apply(a: int, b: int, c: int):
    global apply_callback
    if apply_callback:
        return apply_callback(a, b, c)

def set_apply_callback(fn):
    global apply_callback
    apply_callback = fn

cdef extern int python_native_apply(uint64_t a, uint64_t b, uint64_t c):
    try:
        return apply(a, b, c)
    except Exception as e:
        print('++++++apply return exception:', e)
        import traceback
        traceback.print_exc()
        _eosio_assert(0, str(e))


#chain.h
# uint32_t get_active_producers( uint64_t* producers, uint32_t datalen );
def get_active_producers():
    cdef size_t producers_size = 0
    cdef uint64_t *producers = <uint64_t *>0
    producers_size = _get_active_producers(<uint64_t *>0, 0)
    producers = <uint64_t*>malloc(producers_size)
    _get_active_producers(producers, producers_size)
    ret = PyBytes_FromStringAndSize(<char *>producers, producers_size)
    free(producers)
    return ret

#privileged.h
# void get_resource_limits( uint64_t account, int64_t* ram_bytes, int64_t* net_weight, int64_t* cpu_weight );
def get_resource_limits( uint64_t account):
    cdef int64_t ram_bytes = 0
    cdef int64_t net_weight = 0
    cdef int64_t cpu_weight = 0
    _get_resource_limits(account, &ram_bytes, &net_weight, &cpu_weight)
    return ram_bytes, net_weight, cpu_weight

# void set_resource_limits( uint64_t account, int64_t ram_bytes, int64_t net_weight, int64_t cpu_weight );
def set_resource_limits( uint64_t account, int64_t ram_bytes, int64_t net_weight, int64_t cpu_weight ):
    _set_resource_limits(account, ram_bytes, net_weight, cpu_weight)

# int64_t set_proposed_producers( const char *producer_data, uint32_t producer_data_size );
def set_proposed_producers(producer_data: bytes):
    return _set_proposed_producers(producer_data, len(producer_data))

# int64_t set_proposed_producers_ex( uint64_t producer_data_format, const char *producer_data, uint32_t producer_data_size );
def set_proposed_producers_ex( uint64_t producer_data_format, producer_data: bytes):
    return _set_proposed_producers_ex(producer_data_format, producer_data, len(producer_data))

# bool is_privileged( uint64_t account );
def is_privileged( uint64_t account ):
    return _is_privileged(account)

# void set_privileged( uint64_t account, bool is_priv );
def set_privileged( uint64_t account, bool is_priv ):
    _set_privileged(account, is_priv)

# void set_blockchain_parameters_packed( const char* data, uint32_t datalen );
def set_blockchain_parameters_packed(data: bytes):
    _set_blockchain_parameters_packed(data, len(data))

# uint32_t get_blockchain_parameters_packed( char* data, uint32_t datalen );
def get_blockchain_parameters_packed():
    cdef size_t size = 0
    cdef char *data
    size = _get_blockchain_parameters_packed(<char *>0, 0)
    data = <char *>malloc(size)
    _get_blockchain_parameters_packed(data, size)
    ret = PyBytes_FromStringAndSize(data, size)
    free(data)
    return ret

# void preactivate_feature( const capi_checksum256* feature_digest );
def preactivate_feature(feature_digest: bytes):
    assert(len(feature_digest) == 32)
    return _preactivate_feature(<capi_checksum256 *><char *>feature_digest)


#permission.h
# int32_t check_transaction_authorization( const char* trx_data, uint32_t trx_size,
#                                 const char* pubkeys_data, uint32_t pubkeys_size,
#                                 const char* perms_data,   uint32_t perms_size
#                             );

def check_transaction_authorization(trx_data: bytes, pubkeys_data: bytes, perms_data: bytes):
    return _check_transaction_authorization(trx_data, len(trx_data), pubkeys_data, len(pubkeys_data), perms_data, len(perms_data))

# int32_t check_permission_authorization( uint64_t account,
#                                 uint64_t permission,
#                                 const char* pubkeys_data, uint32_t pubkeys_size,
#                                 const char* perms_data,   uint32_t perms_size,
#                                 uint64_t delay_us
#                             );

def check_permission_authorization(uint64_t account, uint64_t permission, pubkeys_data: bytes, perms_data: bytes, uint64_t delay_us):
    return _check_permission_authorization(account, permission, pubkeys_data, len(pubkeys_data), perms_data, len(perms_data), delay_us)

# int64_t get_permission_last_used( uint64_t account, uint64_t permission );
def get_permission_last_used(uint64_t account, uint64_t permission):
    return _get_permission_last_used(account, permission)

# int64_t get_account_creation_time( uint64_t account );
def get_account_creation_time(uint64_t account):
    return _get_account_creation_time(account)

def prints(const char* cstr):
    _prints(cstr)

#void prints_l( const char* cstr, uint32_t len);
def prints_l(cstr: bytes):
    _prints_l(cstr, len(cstr))

def printi(int64_t value):
    _printi(value)

def printui(uint64_t value):
    _printui(value)

# void printi128( const int128_t* value );
def printi128(value: bytes):
    assert len(value) == 16, "printi128: bad value size"
    _printi128(<int128_t *><char *>value)

# void printui128( const uint128_t* value );
def printui128(value: bytes):
    assert len(value) == 16, "printui128: bad value size"
    _printui128(<uint128_t *><char *>value)

# void printsf(float value);
def printsf(value: bytes):
    assert len(value) == 4, "printsf: bad value size"
    _printsf((<float*><char *>value)[0])

# void printdf(double value);
def printdf(value: bytes):
    _printdf((<double *><char *>value)[0])

# void printqf(const long double* value);
def printqf(value: bytes):
    cdef long double d
    assert len(value) == 16, "printqf: bad value size"
    assert sizeof(d) == 16, "printqf: bad long double size"
    memcpy(&d, <char *>value, 16)
    _printqf(&d)

# void printn( uint64_t name );
def printn( uint64_t name ):
    _printn(name)

# void printhex( const void* data, uint32_t datalen );
def printhex( data: bytes):
    _printhex(<void *><char *>data, len(data))


# uint32_t action_data_size();
def action_data_size():
    return _action_data_size()

def read_action_data():
    cdef uint32_t length = action_data_size()
    data = <char *>malloc(length)
    length = _read_action_data(<void *>data, length)
    ret = PyBytes_FromStringAndSize(data, length)
    free(data)
    return ret

# void require_recipient( uint64_t name );
def require_recipient(uint64_t name):
    _require_recipient(name)

# void require_auth( uint64_t name );
def require_auth(uint64_t name):
    _require_auth(name)

# bool has_auth( uint64_t name );
def has_auth(uint64_t name):
    return _has_auth(name)

# void require_auth2( uint64_t name, uint64_t permission );
def require_auth2(uint64_t name, uint64_t permission):
    _require_auth2(name, permission)

# bool is_account( uint64_t name );
def is_account(uint64_t name):
    return _is_account(name)

def send_inline(serialized_data: bytes):
    _send_inline(serialized_data, len(serialized_data))

def send_context_free_inline(serialized_data: bytes):
    _send_context_free_inline(serialized_data, len(serialized_data))

# uint64_t  publication_time();
def publication_time():
    return _publication_time()

# uint64_t current_receiver();
def current_receiver():
    return _current_receiver()

# void  eosio_assert( uint32_t test, const char* msg );
def eosio_assert(uint32_t test, msg: bytes):
    _eosio_assert(test, <char *>msg)

# void  eosio_assert_message( uint32_t test, const char* msg, uint32_t msg_len );
def eosio_assert_message(uint32_t test, msg: bytes):
    _eosio_assert_message(test, <char *>msg, len(msg))

# void  eosio_assert_code( uint32_t test, uint64_t code );
def eosio_assert_code(uint32_t test, uint64_t code):
    _eosio_assert_code(test, code)

# void eosio_exit( int32_t code );
def eosio_exit( int32_t code ):
    _eosio_exit(code)

# uint64_t  current_time();
def current_time():
    return _current_time()

# bool is_feature_activated( const capi_checksum256* feature_digest );
def is_feature_activated(feature_digest: bytes):
    return _is_feature_activated(<capi_checksum256*><char *>feature_digest)

# uint64_t get_sender();
def get_sender():
    return _get_sender()


# void assert_sha256( const char* data, uint32_t length, const capi_checksum256* hash );
def assert_sha256(data: bytes, hash: bytes):
    assert len(hash) == 32, "assert_sha256: bad hash size"
    _assert_sha256(<char *>data, len(data), <capi_checksum256*><char *>hash)

# void assert_sha1( const char* data, uint32_t length, const capi_checksum160* hash );
def assert_sha1(data: bytes, hash: bytes):
    assert len(hash) == 20, "assert_sha1: bad hash size"
    _assert_sha1(<char *>data, len(data), <capi_checksum160*><char *>hash)

# void assert_sha512( const char* data, uint32_t length, const capi_checksum512* hash );
def assert_sha512(data: bytes, hash: bytes):
    assert len(hash) == 64, "assert_sha512: bad hash size"
    _assert_sha512(<char *>data, len(data), <capi_checksum512*><char *>hash)

# void assert_ripemd160( const char* data, uint32_t length, const capi_checksum160* hash );
def assert_ripemd160(data: bytes, hash: bytes):
    assert len(hash) == 20, "assert_ripemd160: bad hash size"
    _assert_ripemd160(<char *>data, len(data), <capi_checksum160*><char *>hash)

# void sha256( const char* data, uint32_t length, capi_checksum256* hash );
def sha256(data: bytes):
    cdef capi_checksum256 h
    _sha256(<char *>data, len(data), &h)
    return PyBytes_FromStringAndSize(<char *>&h, 32)

# void sha1( const char* data, uint32_t length, capi_checksum160* hash );
def sha1(data: bytes):
    cdef capi_checksum160 h
    _sha1(<char *>data, len(data), &h)
    return PyBytes_FromStringAndSize(<char *>&h, 20)

# void sha512( const char* data, uint32_t length, capi_checksum512* hash );
def sha512(data: bytes):
    cdef capi_checksum512 h
    _sha512(<char *>data, len(data), &h)
    return PyBytes_FromStringAndSize(<char *>&h, 64)

# void ripemd160( const char* data, uint32_t length, capi_checksum160* hash );
def ripemd160(data: bytes):
    cdef capi_checksum160 h
    _ripemd160(<char *>data, len(data), &h)
    return PyBytes_FromStringAndSize(<char *>&h, 20)

# int32_t recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, char* pub, uint32_t publen );
def recover_key(digest: bytes, sig: bytes):
    cdef char pub[34]
    _recover_key(<capi_checksum256*><char *>digest, <char *>sig, len(sig), pub, 34)
    return PyBytes_FromStringAndSize(pub, 34)

# void assert_recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, const char* pub, uint32_t publen );
def assert_recover_key(digest: bytes, sig: bytes, pub: bytes):
    assert len(pub) == 34, "assert_recover_key: bad pub size"
    _assert_recover_key(<capi_checksum256*><char *>digest, <char *>sig, len(sig), <char *>pub, 34)

#transaction.h
# void send_deferred(const uint128_t sender_id, uint64_t payer, const char *serialized_transaction, uint32_t size, uint32_t replace_existing = 0);
def send_deferred(sender_id: bytes, uint64_t payer, serialized_transaction: bytes, uint32_t replace_existing):
    cdef uint128_t _sender_id = 0
    assert len(sender_id) == 16, "send_defered: bad sender_id size"
    memcpy(&_sender_id, <char *>sender_id, 16)
    _send_deferred(_sender_id, payer, <char *>serialized_transaction, len(serialized_transaction), replace_existing)

# int32_t cancel_deferred(const uint128_t sender_id);
def cancel_deferred(sender_id: bytes):
    cdef uint128_t _sender_id
    assert len(sender_id) == 16, "send_defered: bad sender_id size"
    memcpy(&_sender_id, <char *>sender_id, 16)
    return _cancel_deferred(_sender_id)

# uint32_t read_transaction(char *buffer, uint32_t size);
def read_transaction():
    size = transaction_size()
    buffer = <char *>malloc(size)
    _read_transaction(buffer, size)
    ret = PyBytes_FromStringAndSize(buffer, size)
    free(buffer)
    return ret

# uint32_t transaction_size();
def transaction_size():
    return _transaction_size() 

# int32_t tapos_block_num();
def tapos_block_num():
    return _tapos_block_num()

# int32_t tapos_block_prefix();
def tapos_block_prefix():
    return _tapos_block_prefix()

# uint32_t expiration();
def expiration():
    return _expiration()

# int32_t get_action( uint32_t type, uint32_t index, char* buff, uint32_t size );
def get_action( uint32_t _type, uint32_t index):
    size = _get_action(_type, index, <char *>0, 0)
    if size == 0:
        return None
    buff = <char *>malloc(size)
    _get_action(_type, index, buff, size)
    ret = PyBytes_FromStringAndSize(buff, size)
    free(buff)
    return ret

# int32_t get_context_free_data( uint32_t index, char* buff, uint32_t size );
def get_context_free_data(uint32_t index):
    size = _get_context_free_data(index, <char *>0, 0)
    if size == 0:
        return None
    buff = <char *>malloc(size)
    _get_context_free_data(index, buff, size)
    ret = PyBytes_FromStringAndSize(buff, size)
    free(buff)
    return ret

# void _set_action_return_value(const char *data, uint32_t data_size);
def set_action_return_value(data: bytes):
    return _set_action_return_value(data, len(data))

# uint32_t _get_code_hash(capi_name account, uint32_t struct_version, char* packed_result, uint32_t packed_result_len);
def get_code_hash(account: uint64_t, struct_version: int):
    cdef char* packed_result
    cdef uint32_t packed_result_size
    packed_result_size = _get_code_hash(account, struct_version, <char *>0, 0)
    packed_result = <char*>malloc(packed_result_size)
    _get_code_hash(account, struct_version, packed_result, packed_result_size)
    ret = PyBytes_FromStringAndSize(packed_result, packed_result_size)
    free(packed_result)
    return ret

# uint32_t _get_block_num();
def get_block_num():
    return _get_block_num()

# void _sha3( const char* data, uint32_t data_len, char* hash, uint32_t hash_len, int32_t keccak );
def sha3(data: bytes, int32_t keccak ):
    cdef char hash[32]
    _sha3(data, len(data), <char *>hash, 32, keccak)
    return PyBytes_FromStringAndSize(<char *>hash, 32)

# int32_t _blake2_f( uint32_t rounds, const char* state, uint32_t state_len, const char* msg, uint32_t msg_len, 
#                 const char* t0_offset, uint32_t t0_len, const char* t1_offset, uint32_t t1_len, int32_t final, char* result, uint32_t result_len);
def blake2_f(rounds: uint32_t, state: bytes, msg: bytes, t0_offset: bytes, t1_offset: bytes, final: int32_t) -> bytes:
    cdef char result[64]
    if 0 == _blake2_f(rounds, state, len(state), msg, len(msg), t0_offset, len(t0_offset), t1_offset, len(t1_offset), final, result, 64):
        return PyBytes_FromStringAndSize(<char *>result, 64)
    return b''
# int32_t _k1_recover( const char* sig, uint32_t sig_len, const char* dig, uint32_t dig_len, char* pub, uint32_t pub_len);
def k1_recover(sig: bytes, dig: bytes):
    cdef char pub[65]
    if 0 == _k1_recover(sig, len(sig), dig, len(dig), pub, 65):
        return PyBytes_FromStringAndSize(<char *>pub, 65)
    return b''

# int32_t _alt_bn128_add( const char* op1, uint32_t op1_len, const char* op2, uint32_t op2_len, char* result, uint32_t result_len);
def alt_bn128_add(op1: bytes, op2: bytes):
    cdef char result[64]
    if 0 == _alt_bn128_add(op1, len(op1), op2, len(op2), result, 64):
        return PyBytes_FromStringAndSize(<char *>result, 64)
    return b''

# int32_t _alt_bn128_mul( const char* g1, uint32_t g1_len, const char* scalar, uint32_t scalar_len, char* result, uint32_t result_len);
def alt_bn128_mul(g1: bytes, scalar: bytes):
    cdef char result[64]
    if 0 == _alt_bn128_mul(g1, len(g1), scalar, len(scalar), result, 64):
        return PyBytes_FromStringAndSize(<char *>result, 64)
    return b''

# int32_t _alt_bn128_pair( const char* pairs, uint32_t pairs_len);
def alt_bn128_pair(pairs: bytes):
    return _alt_bn128_pair(pairs, len(pairs))

# int32_t _mod_exp( const char* base, uint32_t base_len, const char* exp, uint32_t exp_len, const char* mod, uint32_t mod_len, char* result, uint32_t result_len);
def mod_exp(base: bytes, exp: bytes, mod: bytes):
    cdef char* result
    cdef uint32_t result_size
    result_size = len(mod)
    result = <char *>malloc(result_size)
    _mod_exp(base, len(base), exp, len(exp), mod, len(mod), result, result_size)
    ret = PyBytes_FromStringAndSize(<char *>result, result_size)
    free(result)
    return ret 

def db_store_i64(scope: uint64_t, table: uint64_t, payer: uint64_t, id: uint64_t,  data: bytes):
    return _db_store_i64(scope, table, payer, id,  <void *><const unsigned char *>data, len(data))

def db_update_i64(iterator: int32_t, payer: uint64_t, data: bytes):
    _db_update_i64(iterator, payer, <void *><const char *>data, len(data))

def db_remove_i64(iterator: int32_t):
    _db_remove_i64(iterator)

def db_get_i64(iterator: int32_t):
    cdef char *buffer
    buffer_size = _db_get_i64(iterator, <void*>0, 0)
    buffer = <char *>malloc(buffer_size)
    _db_get_i64(iterator, <void*>buffer, buffer_size)
    ret = PyBytes_FromStringAndSize(buffer, buffer_size)
    free(buffer)
    return ret

def db_next_i64(iterator: int32_t):
    cdef uint64_t primary = 0
    it = _db_next_i64(iterator, &primary)
    return it, primary

def db_previous_i64(iterator: int32_t):
    cdef uint64_t primary = 0
    it = _db_previous_i64(iterator, &primary)
    return it, primary

def db_find_i64(code: uint64_t, scope: uint64_t, table: uint64_t, id: uint64_t):
    return _db_find_i64(code, scope, table, id)

def db_lowerbound_i64(code: uint64_t, scope: uint64_t, table: uint64_t, id: uint64_t):
    return _db_lowerbound_i64(code, scope, table, id)

def db_upperbound_i64(code: uint64_t, scope: uint64_t, table: uint64_t, id: uint64_t):
    return _db_upperbound_i64(code, scope, table, id)

def db_end_i64(code: uint64_t, scope: uint64_t, table: uint64_t):
    return _db_end_i64(code, scope, table)

# int32_t db_idx64_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const uint64_t* secondary);
def db_idx64_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, uint64_t secondary):
    return _db_idx64_store(scope, table, payer, id, &secondary)

# void db_idx64_update(int32_t iterator, uint64_t payer, const uint64_t* secondary);
def db_idx64_update(int32_t iterator, uint64_t payer, uint64_t secondary):
    _db_idx64_update(iterator, payer, &secondary)

# void db_idx64_remove(int32_t iterator);
def db_idx64_remove(int32_t iterator):
    _db_idx64_remove(iterator)

# int32_t db_idx64_next(int32_t iterator, uint64_t* primary);
def db_idx64_next(int32_t iterator):
    cdef uint64_t primary = 0
    it = _db_idx64_next(iterator, &primary)
    return it, primary 

# int32_t db_idx64_previous(int32_t iterator, uint64_t* primary);
def db_idx64_previous(int32_t iteratory):
    cdef uint64_t primary = 0
    it = _db_idx64_previous(iteratory, &primary)
    return it, primary 

# int32_t db_idx64_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t* secondary, uint64_t primary);
def db_idx64_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t primary):
    cdef uint64_t secondary = 0
    it = _db_idx64_find_primary(code, scope, table, &secondary, primary)
    return it, int.to_bytes(secondary, 8, 'little')

# int32_t db_idx64_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint64_t* secondary, uint64_t* primary);
def db_idx64_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint64_t secondary):
    cdef uint64_t primary = 0
    it = _db_idx64_find_secondary(code, scope, table, &secondary, &primary)
    return it, primary

# int32_t db_idx64_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t* secondary, uint64_t* primary);
def db_idx64_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t secondary, uint64_t primary):
    it = _db_idx64_lowerbound(code, scope, table, &secondary, &primary)
    _secondary = PyBytes_FromStringAndSize(<char *>&secondary, 8)
    return it, _secondary, primary

# int32_t db_idx64_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t* secondary, uint64_t* primary);
def db_idx64_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint64_t secondary, uint64_t primary):
    it = _db_idx64_upperbound(code, scope, table, &secondary, &primary)
    _secondary = PyBytes_FromStringAndSize(<char *>&secondary, 8)
    return it, _secondary, primary

# int32_t db_idx64_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx64_end(uint64_t code, uint64_t scope, uint64_t table):
    return _db_idx64_end(code, scope, table)

# int32_t db_idx128_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const uint128_t* secondary);
def db_idx128_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, secondary: bytes):
    assert len(secondary) == 16, "db_idx128_store: bad secondary size"
    return _db_idx128_store(scope, table, payer, id, <uint128_t*><char *>secondary)

# void db_idx128_update(int32_t iterator, uint64_t payer, const uint128_t* secondary);
def db_idx128_update(int32_t iterator, uint64_t payer, secondary: bytes):
    assert len(secondary) == 16, "db_idx128_update: bad secondary size"
    _db_idx128_update(iterator, payer, <uint128_t*><char *>secondary)

# void db_idx128_remove(int32_t iterator);
def db_idx128_remove(int32_t iterator):
    _db_idx128_remove(iterator)

# int32_t db_idx128_next(int32_t iterator, uint64_t* primary);
def db_idx128_next(int32_t iterator):
    cdef uint64_t primary = 0
    it = _db_idx128_next(iterator, &primary)
    return it, primary

# int32_t db_idx128_previous(int32_t iterator, uint64_t* primary);
def db_idx128_previous(int32_t iterator):
    cdef uint64_t primary = 0
    it = _db_idx128_previous(iterator, &primary)
    return it, primary

# int32_t db_idx128_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint128_t* secondary, uint64_t primary);
def db_idx128_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t primary):
    cdef uint128_t secondary = 0
    it = _db_idx128_find_primary(code, scope, table, &secondary, primary)
    return it, PyBytes_FromStringAndSize(<char *>&secondary, 16)

# int32_t db_idx128_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint128_t* secondary, uint64_t* primary);
def db_idx128_find_secondary(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes):
    cdef uint64_t primary = 0
    cdef uint128_t _secondary = 0
    assert len(secondary) == 16, "db_idx128_find_secondary: bad secondary size: %d"%(len(secondary),)
    memcpy(&_secondary, <char *>secondary, 16)
    it = _db_idx128_find_secondary(code, scope, table, &_secondary, &primary)
    return it, primary

# int32_t db_idx128_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* secondary, uint64_t* primary);
def db_idx128_lowerbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef uint128_t _secondary = 0
    assert len(secondary) == 16, "db_idx128_lowerbound: bad secondary size: %d"%(len(secondary),)
    memcpy(&_secondary, <char *>secondary, 16)
    it = _db_idx128_lowerbound(code, scope, table, &_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 16), primary

# int32_t db_idx128_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* secondary, uint64_t* primary);
def db_idx128_upperbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef uint128_t _secondary = 0
    assert len(secondary) == 16, "db_idx128_upperbound: bad secondary size: %d"%(len(secondary),)
    memcpy(&_secondary, <char *>secondary, 16)
    it = _db_idx128_upperbound(code, scope, table, &_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 16), primary

# int32_t db_idx128_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx128_end(uint64_t code, uint64_t scope, uint64_t table):
    return _db_idx128_end(code, scope, table)

# int32_t db_idx256_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const uint128_t* data, uint32_t data_len );
def db_idx256_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, data: bytes):
    assert len(data) == 32, "db_idx256_store: bad data size: %d"%(len(data),)
    return _db_idx256_store(scope, table, payer, id, <uint128_t *><char *>data, 2)

# void db_idx256_update(int32_t iterator, uint64_t payer, const uint128_t* data, uint32_t data_len);
def db_idx256_update(int32_t iterator, uint64_t payer, data: bytes):
    assert len(data) == 32, "db_idx256_update: bad data size: %d"%(len(data),)
    _db_idx256_update(iterator, payer, <uint128_t*><char *>data, 2)

# void db_idx256_remove(int32_t iterator);
def db_idx256_remove(int32_t iterator):
    _db_idx256_remove(iterator)

# int32_t db_idx256_next(int32_t iterator, uint64_t* primary);
def db_idx256_next(int32_t iterator):
    cdef uint64_t primary = 0
    it = _db_idx256_next(iterator, &primary)
    return it, primary

# int32_t db_idx256_previous(int32_t iterator, uint64_t* primary);
def db_idx256_previous(int32_t iterator):
    cdef uint64_t primary = 0
    it = _db_idx256_previous(iterator, &primary)
    return it, primary

# int32_t db_idx256_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint128_t* data, uint32_t data_len, uint64_t primary);
def db_idx256_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t primary):
    cdef uint128_t data[2]
    memset(data, 0, 32)
    it = _db_idx256_find_primary(code, scope, table, data, 2, primary)
    return it, PyBytes_FromStringAndSize(<char *>data, 32)

# int32_t db_idx256_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const uint128_t* data, uint32_t data_len, uint64_t* primary);
def db_idx256_find_secondary(uint64_t code, uint64_t scope, uint64_t table, data: bytes):
    cdef uint64_t primary = 0
    assert len(data) == 32, "db_idx256_find_secondary: bad data size: %d"%(len(data),)
    it = _db_idx256_find_secondary(code, scope, table, <uint128_t*><char *>data, 2, &primary)
    return it, primary

# int32_t db_idx256_lowerbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* data, uint32_t data_len, uint64_t* primary);
def db_idx256_lowerbound(uint64_t code, uint64_t scope, uint64_t table, data: bytes, uint64_t primary):
    cdef uint128_t _data[2]
    assert len(data) == 32, "db_idx256_lowerbound: bad data size: %d"%(len(data),)
    memcpy(_data, <char *>data, 32)
    it = _db_idx256_lowerbound(code, scope, table, _data, 2, &primary)
    return it, PyBytes_FromStringAndSize(<char *>_data, 32), primary

# int32_t db_idx256_upperbound(uint64_t code, uint64_t scope, uint64_t table, uint128_t* data, uint32_t data_len, uint64_t* primary);
def db_idx256_upperbound(uint64_t code, uint64_t scope, uint64_t table, data: bytes, uint64_t primary):
    cdef uint128_t _data[2]
    assert len(data) == 32, "db_idx256_upperbound: bad data size: %d"%(len(data),)
    memcpy(_data, <char *>data, 32)
    it = _db_idx256_upperbound(code, scope, table, _data, 2, &primary)
    return it, PyBytes_FromStringAndSize(<char *>_data, 32), primary

# int32_t db_idx256_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx256_end(uint64_t code, uint64_t scope, uint64_t table):
    return _db_idx256_end(code, scope, table)

# int32_t db_idx_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const double* secondary);
def db_idx_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, secondary: bytes):
    assert len(secondary) == 8, "db_idx_double_store: bad data size: %d"%(len(secondary),)
    return _db_idx_double_store(scope, table, payer, id, <double*><char *>secondary)

# void db_idx_double_update(int32_t iterator, uint64_t payer, const double* secondary);
def db_idx_double_update(int32_t iterator, uint64_t payer, secondary: bytes):
    assert len(secondary) == 8, "db_idx_double_update: bad data size: %d"%(len(secondary),)
    _db_idx_double_update(iterator, payer, <double*><char*>secondary)

# void db_idx_double_remove(int32_t iterator);
def db_idx_double_remove(int32_t iterator):
    _db_idx_double_remove(iterator)

# int32_t db_idx_double_next(int32_t iterator, uint64_t* primary);
def db_idx_double_next(int32_t iterator):
    cdef uint64_t primary = 0
    it = _db_idx_double_next(iterator, &primary)
    return it, primary

# int32_t db_idx_double_previous(int32_t iterator, uint64_t* primary);
def db_idx_double_previous(int32_t iterator):
    cdef uint64_t primary = 0
    it = _db_idx_double_previous(iterator, &primary)
    return it, primary

# int32_t db_idx_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, double* secondary, uint64_t primary);
def db_idx_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t primary):
    cdef double secondary = 0.0
    it = _db_idx_double_find_primary(code, scope, table, &secondary, primary)
    return it, PyBytes_FromStringAndSize(<char*>&secondary, 8)

# int32_t db_idx_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const double* secondary, uint64_t* primary);
def db_idx_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes):
    cdef uint64_t primary = 0
    assert len(secondary) == 8, "db_idx_double_find_secondary:bad secondary size"
    it = _db_idx_double_find_secondary(code, scope, table, <double *><char *>secondary, &primary)
    return it, primary

# int32_t db_idx_double_lowerbound(uint64_t code, uint64_t scope, uint64_t table, double* secondary, uint64_t* primary);
def db_idx_double_lowerbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef double _secondary = 0.0
    assert len(secondary) == 8, "db_idx_double_lowerbound:bad secondary size"
    memcpy(&_secondary, <char *>secondary, 8)
    it = _db_idx_double_lowerbound(code, scope, table, &_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 8), primary

# int32_t db_idx_double_upperbound(uint64_t code, uint64_t scope, uint64_t table, double* secondary, uint64_t* primary);
def db_idx_double_upperbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef double _secondary = 0.0
    assert len(secondary) == 8, "db_idx_double_upperbound:bad secondary size"
    memcpy(&_secondary, <char *>secondary, 8)
    it = _db_idx_double_upperbound(code, scope, table, &_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 8), primary

# int32_t db_idx_double_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx_double_end(uint64_t code, uint64_t scope, uint64_t table):
    return _db_idx_double_end(code, scope, table)

# int32_t db_idx_long_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, const long double* secondary);
def db_idx_long_double_store(uint64_t scope, uint64_t table, uint64_t payer, uint64_t id, secondary: bytes):
    assert len(secondary) == 16, "db_idx_long_double_store:bad secondary size"
    return _db_idx_long_double_store(scope, table, payer, id, <const long double*><char *>secondary)

# void db_idx_long_double_update(int32_t iterator, uint64_t payer, const long double* secondary);
def db_idx_long_double_update(int32_t iterator, uint64_t payer, secondary: bytes):
    assert len(secondary) == 16, "db_idx_long_double_update:bad secondary size"
    _db_idx_long_double_update(iterator, payer, <const long double*><char *>secondary)

# void db_idx_long_double_remove(int32_t iterator);
def db_idx_long_double_remove(int32_t iterator):
    _db_idx_long_double_remove(iterator)

# int32_t db_idx_long_double_next(int32_t iterator, uint64_t* primary);
def db_idx_long_double_next(int32_t iterator):
    cdef uint64_t primary = 0
    it = _db_idx_long_double_next(iterator, &primary)
    return it, primary

# int32_t db_idx_long_double_previous(int32_t iterator, uint64_t* primary);
def db_idx_long_double_previous(int32_t iterator):
    cdef uint64_t primary = 0
    it = _db_idx_long_double_previous(iterator, &primary)
    return it, primary

# int32_t db_idx_long_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, long double* secondary, uint64_t primary);
def db_idx_long_double_find_primary(uint64_t code, uint64_t scope, uint64_t table, uint64_t primary):
    cdef long double secondary = 0.0
    it = _db_idx_long_double_find_primary(code, scope, table, &secondary, primary)
    return it, PyBytes_FromStringAndSize(<char *>&secondary, 16)

# int32_t db_idx_long_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, const long double* secondary, uint64_t* primary);
def db_idx_long_double_find_secondary(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes):
    cdef uint64_t primary = 0
    assert len(secondary) == 16, "db_idx_long_double_find_secondary: bad data size: %d"%(len(secondary),)
    it = _db_idx_long_double_find_secondary(code, scope, table, <long double *><char *>secondary, &primary)
    return it, primary

# int32_t db_idx_long_double_lowerbound(uint64_t code, uint64_t scope, uint64_t table, long double* secondary, uint64_t* primary);
def db_idx_long_double_lowerbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef long double _secondary = 0.0
    assert len(secondary) == 16, "db_idx_long_double_lowerbound:bad secondary size"
    memcpy(&_secondary, <char *>secondary, 16)
    it = _db_idx_long_double_lowerbound(code, scope, table, <long double*>&_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 16), primary

# int32_t db_idx_long_double_upperbound(uint64_t code, uint64_t scope, uint64_t table, long double* secondary, uint64_t* primary);
def db_idx_long_double_upperbound(uint64_t code, uint64_t scope, uint64_t table, secondary: bytes, uint64_t primary):
    cdef long double _secondary = 0.0
    assert len(secondary) == 16, "db_idx_long_double_upperbound:bad secondary size"
    memcpy(&_secondary, <char *>secondary, 16)
    it = _db_idx_long_double_upperbound(code, scope, table, <long double*>&_secondary, &primary)
    return it, PyBytes_FromStringAndSize(<char *>&_secondary, 16), primary

# int32_t db_idx_long_double_end(uint64_t code, uint64_t scope, uint64_t table);
def db_idx_long_double_end(uint64_t code, uint64_t scope, uint64_t table):
    return _db_idx_long_double_end(code, scope, table)
