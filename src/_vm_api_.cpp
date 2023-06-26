#include <Python.h>
#include "_vm_api.hpp"

#define CATCH_AND_SAVE_EXCEPTION() \
catch (...) { \
    save_last_exception(); \
}

vm_api_proxy* api() {
    return get_vm_api_proxy();
}

uint32_t _get_active_producers( capi_name* producers, uint32_t datalen ) {
    try {
        return api()->get_active_producers(producers, datalen);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_store_i64(uint64_t scope, capi_name table, capi_name payer, uint64_t id,  const void* data, uint32_t len) {
    try {
        return api()->db_store_i64(scope, table, payer, id, data, len);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _db_update_i64(int32_t iterator, capi_name payer, const void* data, uint32_t len) {
    try {
        api()->db_update_i64(iterator, payer, data, len);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _db_remove_i64(int32_t iterator) {
    try {
        api()->db_remove_i64(iterator);
    } CATCH_AND_SAVE_EXCEPTION();
}

int32_t _db_get_i64(int32_t iterator, const void* data, uint32_t len) {
    try {
        return api()->db_get_i64(iterator, (void *)data, len);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_next_i64(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_next_i64(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_previous_i64(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_previous_i64(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_find_i64(capi_name code, uint64_t scope, capi_name table, uint64_t id) {
    try {
        return api()->db_find_i64(code, scope, table, id);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_lowerbound_i64(capi_name code, uint64_t scope, capi_name table, uint64_t id) {
    try {
        return api()->db_lowerbound_i64(code, scope, table, id);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_upperbound_i64(capi_name code, uint64_t scope, capi_name table, uint64_t id) {
    try {
        return api()->db_upperbound_i64(code, scope, table, id);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_end_i64(capi_name code, uint64_t scope, capi_name table) {
    try {
        return api()->db_end_i64(code, scope, table);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx64_store(uint64_t scope, capi_name table, capi_name payer, uint64_t id, const uint64_t* secondary) {
    try {
        return api()->db_idx64_store(scope, table, payer, id, secondary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _db_idx64_update(int32_t iterator, capi_name payer, const uint64_t* secondary) {
    try {
        api()->db_idx64_update(iterator, payer, secondary);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _db_idx64_remove(int32_t iterator) {
    try {
        api()->db_idx64_remove(iterator);
    } CATCH_AND_SAVE_EXCEPTION();
}

int32_t _db_idx64_next(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_idx64_next(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx64_previous(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_idx64_previous(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx64_find_primary(capi_name code, uint64_t scope, capi_name table, uint64_t* secondary, uint64_t primary) {
    try {
        return api()->db_idx64_find_primary(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx64_find_secondary(capi_name code, uint64_t scope, capi_name table, const uint64_t* secondary, uint64_t* primary) {
    try {
        return api()->db_idx64_find_secondary(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx64_lowerbound(capi_name code, uint64_t scope, capi_name table, uint64_t* secondary, uint64_t* primary) {
    try {
        return api()->db_idx64_lowerbound(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx64_upperbound(capi_name code, uint64_t scope, capi_name table, uint64_t* secondary, uint64_t* primary) {
    try {
        return api()->db_idx64_upperbound(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx64_end(capi_name code, uint64_t scope, capi_name table) {
    try {
        return api()->db_idx64_end(code, scope, table);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx128_store(uint64_t scope, capi_name table, capi_name payer, uint64_t id, const uint128_t* secondary) {
    try {
        return api()->db_idx128_store(scope, table, payer, id, secondary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _db_idx128_update(int32_t iterator, capi_name payer, const uint128_t* secondary) {
    try {
        api()->db_idx128_update(iterator, payer, secondary);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _db_idx128_remove(int32_t iterator) {
    try {
        api()->db_idx128_remove(iterator);
    } CATCH_AND_SAVE_EXCEPTION();
}

int32_t _db_idx128_next(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_idx128_next(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx128_previous(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_idx128_previous(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx128_find_primary(capi_name code, uint64_t scope, capi_name table, uint128_t* secondary, uint64_t primary) {
    try {
        return api()->db_idx128_find_primary(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx128_find_secondary(capi_name code, uint64_t scope, capi_name table, const uint128_t* secondary, uint64_t* primary) {
    try {
        return api()->db_idx128_find_secondary(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx128_lowerbound(capi_name code, uint64_t scope, capi_name table, uint128_t* secondary, uint64_t* primary) {
    try {
        return api()->db_idx128_lowerbound(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx128_upperbound(capi_name code, uint64_t scope, capi_name table, uint128_t* secondary, uint64_t* primary) {
    try {
        return api()->db_idx128_upperbound(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx128_end(capi_name code, uint64_t scope, capi_name table) {
    try {
        return api()->db_idx128_end(code, scope, table);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx256_store(uint64_t scope, capi_name table, capi_name payer, uint64_t id, const uint128_t* data, uint32_t data_len ) {
    try {
        return api()->db_idx256_store(scope, table, payer, id, data, data_len);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _db_idx256_update(int32_t iterator, capi_name payer, const uint128_t* data, uint32_t data_len) {
    try {
        api()->db_idx256_update(iterator, payer, data, data_len);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _db_idx256_remove(int32_t iterator) {
    try {
        api()->db_idx256_remove(iterator);
    } CATCH_AND_SAVE_EXCEPTION();
}

int32_t _db_idx256_next(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_idx256_next(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx256_previous(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_idx256_previous(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx256_find_primary(capi_name code, uint64_t scope, capi_name table, uint128_t* data, uint32_t data_len, uint64_t primary) {
    try {
        return api()->db_idx256_find_primary(code, scope, table, data, data_len, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx256_find_secondary(capi_name code, uint64_t scope, capi_name table, const uint128_t* data, uint32_t data_len, uint64_t* primary) {
    try {
        return api()->db_idx256_find_secondary(code, scope, table, data, data_len, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx256_lowerbound(capi_name code, uint64_t scope, capi_name table, uint128_t* data, uint32_t data_len, uint64_t* primary) {
    try {
        return api()->db_idx256_lowerbound(code, scope, table, data, data_len, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx256_upperbound(capi_name code, uint64_t scope, capi_name table, uint128_t* data, uint32_t data_len, uint64_t* primary) {
    try {
        return api()->db_idx256_upperbound(code, scope, table, data, data_len, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx256_end(capi_name code, uint64_t scope, capi_name table) {
    try {
        return api()->db_idx256_end(code, scope, table);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_double_store(uint64_t scope, capi_name table, capi_name payer, uint64_t id, const double* secondary) {
    try {
        return api()->db_idx_double_store(scope, table, payer, id, secondary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _db_idx_double_update(int32_t iterator, capi_name payer, const double* secondary) {
    try {
        api()->db_idx_double_update(iterator, payer, secondary);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _db_idx_double_remove(int32_t iterator) {
    try {
        api()->db_idx_double_remove(iterator);
    } CATCH_AND_SAVE_EXCEPTION();
}

int32_t _db_idx_double_next(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_idx_double_next(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_double_previous(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_idx_double_previous(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_double_find_primary(capi_name code, uint64_t scope, capi_name table, double* secondary, uint64_t primary) {
    try {
        return api()->db_idx_double_find_primary(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_double_find_secondary(capi_name code, uint64_t scope, capi_name table, const double* secondary, uint64_t* primary) {
    try {
        return api()->db_idx_double_find_secondary(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_double_lowerbound(capi_name code, uint64_t scope, capi_name table, double* secondary, uint64_t* primary) {
    try {
        return api()->db_idx_double_lowerbound(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_double_upperbound(capi_name code, uint64_t scope, capi_name table, double* secondary, uint64_t* primary) {
    try {
        return api()->db_idx_double_upperbound(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_double_end(capi_name code, uint64_t scope, capi_name table) {
    try {
        return api()->db_idx_double_end(code, scope, table);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_long_double_store(uint64_t scope, capi_name table, capi_name payer, uint64_t id, const long double* secondary) {
    try {
        return api()->db_idx_long_double_store(scope, table, payer, id, secondary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _db_idx_long_double_update(int32_t iterator, capi_name payer, const long double* secondary) {
    try {
        api()->db_idx_long_double_update(iterator, payer, secondary);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _db_idx_long_double_remove(int32_t iterator) {
    try {
        api()->db_idx_long_double_remove(iterator);
    } CATCH_AND_SAVE_EXCEPTION();
}

int32_t _db_idx_long_double_next(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_idx_long_double_next(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_long_double_previous(int32_t iterator, uint64_t* primary) {
    try {
        return api()->db_idx_long_double_previous(iterator, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_long_double_find_primary(capi_name code, uint64_t scope, capi_name table, long double* secondary, uint64_t primary) {
    try {
        return api()->db_idx_long_double_find_primary(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_long_double_find_secondary(capi_name code, uint64_t scope, capi_name table, const long double* secondary, uint64_t* primary) {
    try {
        return api()->db_idx_long_double_find_secondary(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_long_double_lowerbound(capi_name code, uint64_t scope, capi_name table, long double* secondary, uint64_t* primary) {
    try {
        return api()->db_idx_long_double_lowerbound(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_long_double_upperbound(capi_name code, uint64_t scope, capi_name table, long double* secondary, uint64_t* primary) {
    try {
        return api()->db_idx_long_double_upperbound(code, scope, table, secondary, primary);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _db_idx_long_double_end(capi_name code, uint64_t scope, capi_name table) {
    try {
        return api()->db_idx_long_double_end(code, scope, table);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _check_transaction_authorization( const char* trx_data,     uint32_t trx_size, const char* pubkeys_data, uint32_t pubkeys_size,const char* perms_data,   uint32_t perms_size) {
    try {
        return api()->check_transaction_authorization(trx_data, trx_size, pubkeys_data, pubkeys_size, perms_data, perms_size);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _check_permission_authorization( capi_name account, capi_name permission, const char* pubkeys_data, uint32_t pubkeys_size, const char* perms_data,   uint32_t perms_size, uint64_t delay_us) {
    try {
        return api()->check_permission_authorization(account, permission, pubkeys_data, pubkeys_size, perms_data, perms_size, delay_us);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int64_t _get_permission_last_used( capi_name account, capi_name permission ) {
    try {
        return api()->get_permission_last_used(account, permission);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int64_t _get_account_creation_time( capi_name account ) {
    try {
        return api()->get_account_creation_time(account);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _assert_sha256( const char* data, uint32_t length, const capi_checksum256* hash ) {
    try {
        api()->assert_sha256(data, length, hash);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _assert_sha1( const char* data, uint32_t length, const capi_checksum160* hash ) {
    try {
        api()->assert_sha1(data, length, hash);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _assert_sha512( const char* data, uint32_t length, const capi_checksum512* hash ) {
    try {
        api()->assert_sha512(data, length, hash);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _assert_ripemd160( const char* data, uint32_t length, const capi_checksum160* hash ) {
    try {
        api()->assert_ripemd160(data, length, hash);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _sha256( const char* data, uint32_t length, capi_checksum256* hash ) {
    try {
        api()->sha256(data, length, hash);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _sha1( const char* data, uint32_t length, capi_checksum160* hash ) {
    try {
        api()->sha1(data, length, hash);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _sha512( const char* data, uint32_t length, capi_checksum512* hash ) {
    try {
        api()->sha512(data, length, hash);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _ripemd160( const char* data, uint32_t length, capi_checksum160* hash ) {
    try {
        api()->ripemd160(data, length, hash);
    } CATCH_AND_SAVE_EXCEPTION();
}

int _recover_key( const capi_checksum256* digest, const char* sig, size_t siglen, char* pub, size_t publen ) {
    try {
        return api()->recover_key(digest, sig, siglen, pub, publen);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _assert_recover_key( const capi_checksum256* digest, const char* sig, size_t siglen, const char* pub, size_t publen ) {
    try {
        api()->assert_recover_key(digest, sig, siglen, pub, publen);
    } CATCH_AND_SAVE_EXCEPTION();
}

uint32_t _read_action_data( void* msg, uint32_t len ) {
    try {
        return api()->read_action_data(msg, len);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

uint32_t _action_data_size() {
    try {
        return api()->action_data_size();
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _require_recipient( capi_name name ) {
    try {
        api()->require_recipient(name);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _require_auth( capi_name name ) {
    try {
        api()->require_auth(name);
    } CATCH_AND_SAVE_EXCEPTION();
}

bool _has_auth( capi_name name ) {
    try {
        return api()->has_auth(name);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _require_auth2( capi_name name, capi_name permission ) {
    try {
        api()->require_auth2(name, permission);
    } CATCH_AND_SAVE_EXCEPTION();
}

bool _is_account( capi_name name ) {
    try {
        return api()->is_account(name);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _send_inline(char *serialized_action, size_t size) {
    try {
        api()->send_inline(serialized_action, size);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _send_context_free_inline(char *serialized_action, size_t size) {
    try {
        api()->send_context_free_inline(serialized_action, size);
    } CATCH_AND_SAVE_EXCEPTION();
}

uint64_t _publication_time() {
    try {
        return api()->publication_time();
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

capi_name _current_receiver() {
    try {
        return api()->current_receiver();
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _prints( const char* cstr ) {
    try {
        api()->prints(cstr);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _prints_l( const char* cstr, uint32_t len) {
    try {
        api()->prints_l(cstr, len);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _printi( int64_t value ) {
    try {
        api()->printi(value);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _printui( uint64_t value ) {
    try {
        api()->printui(value);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _printi128( const int128_t* value ) {
    try {
        api()->printi128(value);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _printui128( const uint128_t* value ) {
    try {
        api()->printui128(value);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _printsf(float value) {
    try {
        api()->printsf(value);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _printdf(double value) {
    try {
        api()->printdf(value);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _printqf(const long double* value) {
    try {
        api()->printqf(value);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _printn( uint64_t name ) {
    try {
        api()->printn(name);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _printhex( const void* data, uint32_t datalen ) {
    try {
        api()->printhex(data, datalen);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _eosio_assert( uint32_t test, const char* msg ) {
    try {
        api()->eosio_assert(test, msg);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _eosio_assert_message( uint32_t test, const char* msg, uint32_t msg_len ) {
    try {
        api()->eosio_assert_message(test, msg, msg_len);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _eosio_assert_code( uint32_t test, uint64_t code ) {
    try {
        api()->eosio_assert_code(test, code);
    } CATCH_AND_SAVE_EXCEPTION();
}

uint64_t _current_time() {
    try {
        return api()->current_time();
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

bool _is_feature_activated( const capi_checksum256* feature_digest ) {
    try {
        return api()->is_feature_activated(feature_digest);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

capi_name _get_sender() {
    try {
        return api()->get_sender();
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _get_resource_limits( capi_name account, int64_t* ram_bytes, int64_t* net_weight, int64_t* cpu_weight ) {
    try {
        api()->get_resource_limits(account, ram_bytes, net_weight, cpu_weight);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _set_resource_limits( capi_name account, int64_t ram_bytes, int64_t net_weight, int64_t cpu_weight ) {
    try {
        api()->set_resource_limits(account, ram_bytes, net_weight, cpu_weight);
    } CATCH_AND_SAVE_EXCEPTION();
}

int64_t _set_proposed_producers( char *producer_data, uint32_t producer_data_size ) {
    try {
        return api()->set_proposed_producers(producer_data, producer_data_size);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int64_t _set_proposed_producers_ex( uint64_t producer_data_format, char *producer_data, uint32_t producer_data_size ) {
    try {
        return api()->set_proposed_producers_ex(producer_data_format, producer_data, producer_data_size);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

bool _is_privileged( capi_name account ) {
    try {
        return api()->is_privileged(account);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _set_privileged( capi_name account, bool is_priv ) {
    try {
        api()->set_privileged(account, is_priv);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _set_blockchain_parameters_packed( char* data, uint32_t datalen ) {
    try {
        api()->set_blockchain_parameters_packed(data, datalen);
    } CATCH_AND_SAVE_EXCEPTION();
}

uint32_t _get_blockchain_parameters_packed( char* data, uint32_t datalen ) {
    try {
        return api()->get_blockchain_parameters_packed(data, datalen);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _preactivate_feature( const capi_checksum256* feature_digest ) {
    try {
        api()->preactivate_feature(feature_digest);
    } CATCH_AND_SAVE_EXCEPTION();
}

void _send_deferred(const uint128_t& sender_id, capi_name payer, const char *serialized_transaction, size_t size, uint32_t replace_existing) {
    try {
        api()->send_deferred(sender_id, payer, serialized_transaction, size, 0);
    } CATCH_AND_SAVE_EXCEPTION();
}

int _cancel_deferred(const uint128_t& sender_id) {
    try {
        return api()->cancel_deferred(sender_id);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

size_t _read_transaction(char *buffer, size_t size) {
    try {
        return api()->read_transaction(buffer, size);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

size_t _transaction_size() {
    try {
        return api()->transaction_size();
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int _tapos_block_num() {
    try {
        return api()->tapos_block_num();
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int _tapos_block_prefix() {
    try {
        return api()->tapos_block_prefix();
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

uint32_t _expiration() {
    try {
        return api()->expiration();
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int _get_action( uint32_t type, uint32_t index, char* buff, size_t size ) {
    try {
        return api()->get_action(type, index, buff, size);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int _get_context_free_data( uint32_t index, char* buff, size_t size ) {
    try {
        return api()->get_context_free_data(index, buff, size);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _eosio_exit( int32_t code ) {
    try {
        api()->eosio_exit(code);
    } CATCH_AND_SAVE_EXCEPTION();
}


void _set_action_return_value(const char *data, uint32_t data_size) {
    try {
        api()->set_action_return_value(data, data_size);
    } CATCH_AND_SAVE_EXCEPTION();
}

uint32_t _get_code_hash(capi_name account, uint32_t struct_version, char* packed_result, uint32_t packed_result_len) {
    try {
        return api()->get_code_hash(account, struct_version, packed_result, packed_result_len);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

uint32_t _get_block_num() {
    try {
        return api()->get_block_num();
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

void _sha3( const char* data, uint32_t data_len, char* hash, uint32_t hash_len, int32_t keccak ) {
    try {
        api()->sha3(data, data_len, hash, hash_len, keccak);
    } CATCH_AND_SAVE_EXCEPTION();
}

int32_t _blake2_f( uint32_t rounds, const char* state, uint32_t state_len, const char* msg, uint32_t msg_len, 
                const char* t0_offset, uint32_t t0_len, const char* t1_offset, uint32_t t1_len, int32_t final, char* result, uint32_t result_len) {
    try {
        return api()->blake2_f(rounds, state, state_len, msg, msg_len, t0_offset, t0_len, t1_offset, t1_len, final, result, result_len);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _k1_recover( const char* sig, uint32_t sig_len, const char* dig, uint32_t dig_len, char* pub, uint32_t pub_len) {
    try {
        return api()->k1_recover(sig, sig_len, dig, dig_len, pub, pub_len);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _alt_bn128_add( const char* op1, uint32_t op1_len, const char* op2, uint32_t op2_len, char* result, uint32_t result_len) {
    try {
        return api()->alt_bn128_add(op1, op1_len, op2, op2_len, result, result_len);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _alt_bn128_mul( const char* g1, uint32_t g1_len, const char* scalar, uint32_t scalar_len, char* result, uint32_t result_len) {
    try {
        return api()->alt_bn128_mul(g1, g1_len, scalar, scalar_len, result, result_len);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _alt_bn128_pair( const char* pairs, uint32_t pairs_len) {
    try {
        return api()->alt_bn128_pair(pairs, pairs_len);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}

int32_t _mod_exp( const char* base, uint32_t base_len, const char* exp, uint32_t exp_len, const char* mod, uint32_t mod_len, char* result, uint32_t result_len) {
    try {
        return api()->mod_exp(base, base_len, exp, exp_len, mod, mod_len, result, result_len);
    } CATCH_AND_SAVE_EXCEPTION();
    return 0;
}
