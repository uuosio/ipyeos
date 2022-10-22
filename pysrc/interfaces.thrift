namespace cpp chaintester
namespace d chaintester
namespace dart chaintester
namespace java chaintester
namespace php chaintester
namespace perl chaintester
namespace haxe chaintester
namespace netstd chaintester

exception TransactionException {
  1: string exc
}

exception AssertException {
  1: string error_message
}

union ActionArguments {
   1: binary raw_args
   2: string json_args
}

service IPCChainTester {
   oneway void init_vm_api()
   oneway void init_apply_request()

   void enable_debug_contract(1:i32 id, 2:string contract, 3:bool enable)
   bool is_debug_contract_enabled(1:i32 id, 2:string contract)

   binary pack_abi(1:string abi)

   binary pack_action_args(1:i32 id, 2:string contract, 3:string action, 4:string action_args)
   binary unpack_action_args(1:i32 id, 2:string contract, 3:string action, 4:binary raw_args)

   i32 new_chain(1:bool initialize)
   i32 free_chain(1:i32 id)
   string get_info(1:i32 id)
   string create_key(1:string key_type)
   string get_account(1:i32 id, 2:string account)
   string create_account(1:i32 id, 2:string creator, 3:string account, 4:string owner_key, 5:string active_key, 6:i64 ram_bytes, 7:i64 stake_net, 8:i64 stake_cpu)
   bool import_key(1:i32 id, 2:string pub_key, 3:string priv_key)
   string get_required_keys(1:i32 id, 2:string transaction, 3:list<string> available_keys)

   void produce_block(1:i32 id, 2:i64 next_block_skip_seconds),
   binary push_action(1:i32 id, 2:string account, 3:string action, 4:ActionArguments arguments, 5: string permissions)
   binary push_actions(1:i32 id, 2:list<Action> actions)
   binary deploy_contract(1:i32 id, 2:string account, 3:string wasm, 4:string abi)

   string get_table_rows(1:i32 id, 2:bool json, 3:string code, 4:string scope, 5:string table,
                                    6:string lower_bound, 7:string upper_bound,
                                    8:i64 limit,
                                    9:string key_type,
                                    10:string index_position,
                                    11:bool reverse,
                                    12:bool show_payer)
}

struct Action {
  1: string account
  2: string action
  3: string permissions
  4: ActionArguments arguments
}

struct Uint64 {
  1: binary rawValue
}

struct DataBuffer {
  1: i32 size
  2: binary buffer
}

struct NextPreviousReturn {
  1: i32 iterator
  2: Uint64 primary
}

struct IteratorPrimaryReturn {
  1: i32 iterator
  2: Uint64 primary
}

struct FindPrimaryReturn {
  1: i32 iterator
  2: binary secondary
}

struct FindSecondaryReturn {
  1: i32 iterator
  2: Uint64 primary
}

struct LowerBoundUpperBoundReturn {
  1: i32 iterator
  2: binary secondary
  3: Uint64 primary
}

struct GetResourceLimitsReturn {
   1:i64 ram_bytes
   2:i64 net_weight
   3:i64 cpu_weight
}

service PushActions {
   i32 push_actions(1:list<Action> actions),
}

service ApplyRequest {
   i32 apply_request(1:Uint64 receiver, 2:Uint64 firstReceiver, 3:Uint64 action),
   i32 apply_end(),
}

service Apply {
   i32 end_apply(),

#chain.h
# uint32_t get_active_producers( uint64_t* producers, uint32_t datalen );
   binary get_active_producers(),
#privileged.h
# void get_resource_limits( uint64_t account, int64_t* ram_bytes, int64_t* net_weight, int64_t* cpu_weight );
   GetResourceLimitsReturn get_resource_limits(1:Uint64 account),
# void set_resource_limits( uint64_t account, int64_t ram_bytes, int64_t net_weight, int64_t cpu_weight );
   void set_resource_limits(1:Uint64 account, 2:i64 ram_bytes, 3:i64 net_weight, 4:i64 cpu_weight ),
# int64_t set_proposed_producers( const char *producer_data, uint32_t producer_data_size );
   i64 set_proposed_producers(1:binary producer_data),
# int64_t set_proposed_producers_ex( uint64_t producer_data_format, const char *producer_data, uint32_t producer_data_size );
   i64 set_proposed_producers_ex(1:Uint64 producer_data_format, 2:binary producer_data),
# bool is_privileged( uint64_t account );
   bool is_privileged(1:Uint64 account),
# void set_privileged( uint64_t account, bool is_priv );
   void set_privileged(1:Uint64 account, 2:bool is_priv),
# void set_blockchain_parameters_packed( const char* data, uint32_t datalen );
   void set_blockchain_parameters_packed(1:binary data),
# uint32_t get_blockchain_parameters_packed( char* data, uint32_t datalen );
   binary get_blockchain_parameters_packed(),
# void preactivate_feature( const capi_checksum256* feature_digest );
   void preactivate_feature(1:binary feature_digest),
#permission.h
# int32_t check_transaction_authorization( const char* trx_data, uint32_t trx_size,
#                                 const char* pubkeys_data, uint32_t pubkeys_size,
#                                 const char* perms_data,   uint32_t perms_size
#                             );
   i32 check_transaction_authorization(1:binary trx_data, 2:binary pubkeys_data, 3:binary perms_data),
# int32_t check_permission_authorization( uint64_t account,
#                                 uint64_t permission,
#                                 const char* pubkeys_data, uint32_t pubkeys_size,
#                                 const char* perms_data,   uint32_t perms_size,
#                                 uint64_t delay_us
#                             );
   i32 check_permission_authorization(1:Uint64 account, 2:Uint64 permission, 3:binary pubkeys_data, 4:binary perms_data, 5:Uint64 delay_us),
# int64_t get_permission_last_used( uint64_t account, uint64_t permission );
   i64 get_permission_last_used(1:Uint64 account, 2:Uint64 permission),
# int64_t get_account_creation_time( uint64_t account );
   i64 get_account_creation_time(1:Uint64 account),
   void prints(1:string cstr),
   void prints_l(1:binary cstr),
   void printi(1:i64 n),
   void printui(1:Uint64 n),
   void printi128(1:binary value),
   void printui128(1:binary value),
   void printsf(1:binary value),
   void printdf(1:binary value),
   void printqf(1:binary value),
   void printn(1:Uint64 name),
   void printhex(1:binary data),

   i32 action_data_size(),
   binary read_action_data(),
   void require_recipient(1:Uint64 name),
   void require_auth(1:Uint64 name),
   bool has_auth(1:Uint64 name),
   void require_auth2(1:Uint64 name, 2:Uint64 permission),
   bool is_account(1:Uint64 name),
   void send_inline(1:binary serialized_action),
   void send_context_free_inline(1:binary serialized_data),
   Uint64 publication_time(),
   Uint64 current_receiver(),

  # void  eosio_assert( uint32_t test, const char* msg );
   void eosio_assert(1:bool test, 2:binary msg),
  # void  eosio_assert_message( uint32_t test, const char* msg, uint32_t msg_len );
   void eosio_assert_message(1:bool test, 2:binary msg),
  # void  eosio_assert_code( uint32_t test, uint64_t code );
   void eosio_assert_code(1:bool test, 2:Uint64 code),
  # void eosio_exit( int32_t code );
   void eosio_exit(1:i32 code ),
  # uint64_t  current_time();
   Uint64 current_time(),
  # bool is_feature_activated( const capi_checksum256* feature_digest );
   bool is_feature_activated(1:binary feature_digest),
  # uint64_t get_sender();
   Uint64 get_sender(),


# void assert_sha256( const char* data, uint32_t length, const capi_checksum256* hash );
   void assert_sha256(1:binary data, 2:binary hash),
# void assert_sha1( const char* data, uint32_t length, const capi_checksum160* hash );
   void assert_sha1(1:binary data, 2:binary hash),
# void assert_sha512( const char* data, uint32_t length, const capi_checksum512* hash );
   void assert_sha512(1:binary data, 2:binary hash),

# void assert_ripemd160( const char* data, uint32_t length, const capi_checksum160* hash );
   void assert_ripemd160(1:binary data, 2:binary hash),

# void sha256( const char* data, uint32_t length, capi_checksum256* hash );
   binary sha256(1:binary data),
# void sha1( const char* data, uint32_t length, capi_checksum160* hash );
   binary sha1(1:binary data),
# void sha512( const char* data, uint32_t length, capi_checksum512* hash );
   binary sha512(1:binary data),
# void ripemd160( const char* data, uint32_t length, capi_checksum160* hash );
   binary ripemd160(1:binary data),
# int32_t recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, char* pub, uint32_t publen );
   binary recover_key(1:binary digest, 2:binary sig),
# void assert_recover_key( const capi_checksum256* digest, const char* sig, uint32_t siglen, const char* pub, uint32_t publen );
   void assert_recover_key(1:binary digest, 2:binary sig, 3:binary pub),


#transaction.h
# void send_deferred(const uint128_t sender_id, uint64_t payer, const char *serialized_transaction, uint32_t size, uint32_t replace_existing = 0);
   void send_deferred(1:binary sender_id, 2:Uint64 payer, 3:binary serialized_transaction, 4: i32 replace_existing),
# int32_t cancel_deferred(const uint128_t sender_id);
   i32 cancel_deferred(1:binary sender_id),
# uint32_t read_transaction(char *buffer, uint32_t size);
   binary read_transaction(),
# uint32_t transaction_size();
   i32 transaction_size(),
# int32_t tapos_block_num();
   i32 tapos_block_num(),
# int32_t tapos_block_prefix();
   i32 tapos_block_prefix(),
# uint32_t expiration();
   i64 expiration(),
# int32_t get_action( uint32_t type, uint32_t index, char* buff, uint32_t size );
   binary get_action(1:i32 _type, 2:i32 index),
# int32_t get_context_free_data( uint32_t index, char* buff, uint32_t size );
   binary get_context_free_data(1:i32 index),

   i32 db_store_i64(1:Uint64 scope, 2:Uint64 table, 3:Uint64 payer, 4:Uint64 id,  5:binary data),
   void db_update_i64(1:i32 iterator, 2:Uint64 payer, 3:binary data),
   void db_remove_i64(1:i32 iterator),
   binary db_get_i64(1:i32 iterator),
   NextPreviousReturn db_next_i64(1:i32 iterator),
   NextPreviousReturn db_previous_i64(1:i32 iterator),
   i32 db_find_i64(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:Uint64 id),
   i32 db_lowerbound_i64(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:Uint64 id),
   i32 db_upperbound_i64(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:Uint64 id),
   i32 db_end_i64(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table),

   i32 db_idx64_store(1:Uint64 scope, 2:Uint64 table, 3:Uint64 payer, 4:Uint64 id, 5:Uint64 secondary),
   void db_idx64_update(1:i32 iterator, 2:Uint64 payer, 3:Uint64 secondary),
   void db_idx64_remove(1:i32 iterator),
   NextPreviousReturn db_idx64_next(1:i32 iterator),
   NextPreviousReturn db_idx64_previous(1:i32 iteratory),
   FindPrimaryReturn db_idx64_find_primary(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:Uint64 primary),
   FindSecondaryReturn db_idx64_find_secondary(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:Uint64 secondary),
   LowerBoundUpperBoundReturn db_idx64_lowerbound(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:Uint64 secondary, 5:Uint64 primary),
   LowerBoundUpperBoundReturn db_idx64_upperbound(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:Uint64 secondary, 5:Uint64 primary),
   i32 db_idx64_end(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table),

   i32 db_idx128_store(1:Uint64 scope, 2:Uint64 table, 3:Uint64 payer, 4:Uint64 id, 5:binary secondary),
   void db_idx128_update(1:i32 iterator, 2:Uint64 payer, 3:binary secondary),
   void db_idx128_remove(1:i32 iterator),
   NextPreviousReturn db_idx128_next(1:i32 iterator),
   NextPreviousReturn db_idx128_previous(1:i32 iterator),
   FindPrimaryReturn db_idx128_find_primary(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:Uint64 primary),
   FindSecondaryReturn db_idx128_find_secondary(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary secondary),
   LowerBoundUpperBoundReturn db_idx128_lowerbound(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary secondary, 5:Uint64 primary),
   LowerBoundUpperBoundReturn db_idx128_upperbound(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary secondary, 5:Uint64 primary),
   i32 db_idx128_end(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table),
   i32 db_idx256_store(1:Uint64 scope, 2:Uint64 table, 3:Uint64 payer, 4:Uint64 id, 5:binary data),
   void db_idx256_update(1:i32 iterator, 2:Uint64 payer, 3:binary data),
   void db_idx256_remove(1:i32 iterator),
   NextPreviousReturn db_idx256_next(1:i32 iterator),
   NextPreviousReturn db_idx256_previous(1:i32 iterator),
   FindPrimaryReturn db_idx256_find_primary(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:Uint64 primary),
   FindSecondaryReturn db_idx256_find_secondary(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary data),
   LowerBoundUpperBoundReturn db_idx256_lowerbound(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary data, 5:Uint64 primary),
   LowerBoundUpperBoundReturn db_idx256_upperbound(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary data, 5:Uint64 primary),
   i32 db_idx256_end(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table),
   i32 db_idx_double_store(1:Uint64 scope, 2:Uint64 table, 3:Uint64 payer, 4:Uint64 id, 5:binary secondary),
   void db_idx_double_update(1:i32 iterator, 2:Uint64 payer, 3:binary secondary),
   void db_idx_double_remove(1:i32 iterator),
   NextPreviousReturn db_idx_double_next(1:i32 iterator),
   NextPreviousReturn db_idx_double_previous(1:i32 iterator),
   FindPrimaryReturn db_idx_double_find_primary(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:Uint64 primary),
   FindSecondaryReturn db_idx_double_find_secondary(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary secondary),
   LowerBoundUpperBoundReturn db_idx_double_lowerbound(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary secondary, 5:Uint64 primary),
   LowerBoundUpperBoundReturn db_idx_double_upperbound(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary secondary, 5:Uint64 primary),
   i32 db_idx_double_end(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table),

   i32 db_idx_long_double_store(1:Uint64 scope, 2:Uint64 table, 3:Uint64 payer, 4:Uint64 id, 5:binary secondary),
   void db_idx_long_double_update(1:i32 iterator, 2:Uint64 payer, 3:binary secondary),
   void db_idx_long_double_remove(1:i32 iterator),
   NextPreviousReturn db_idx_long_double_next(1:i32 iterator),
   NextPreviousReturn db_idx_long_double_previous(1:i32 iterator),
   FindPrimaryReturn db_idx_long_double_find_primary(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:Uint64 primary),
   FindSecondaryReturn db_idx_long_double_find_secondary(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary secondary),
   LowerBoundUpperBoundReturn db_idx_long_double_lowerbound(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary secondary, 5:Uint64 primary),
   LowerBoundUpperBoundReturn db_idx_long_double_upperbound(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table, 4:binary secondary, 5:Uint64 primary),
   i32 db_idx_long_double_end(1:Uint64 code, 2:Uint64 scope, 3:Uint64 table),

   // void set_action_return_value(const char *data, uint32_t data_size);
   void set_action_return_value(1:binary data),
   // uint32_t get_code_hash(capi_name account, uint32_t struct_version, char* packed_result, uint32_t packed_result_len);
   binary get_code_hash(1:Uint64 account, 2:i64 struct_version),
   // uint32_t get_block_num();
   i64 get_block_num(),
   // void sha3( const char* data, uint32_t data_len, char* hash, uint32_t hash_len, int32_t keccak );
   binary sha3(1:binary data, 2:i32 keccak),
   binary blake2_f(1:i64 rounds, 2:binary state, 3:binary msg, 4:binary t0_offset, 5:binary t1_offset, 6:i32 final),
   // int32_t k1_recover( const char* sig, uint32_t sig_len, const char* dig, uint32_t dig_len, char* pub, uint32_t pub_len);
   binary k1_recover(1:binary sig, 2:binary dig,),
   // int32_t alt_bn128_add( const char* op1, uint32_t op1_len, const char* op2, uint32_t op2_len, char* result, uint32_t result_len);
   binary alt_bn128_add(1:binary op1, 2:binary op2),
   // int32_t alt_bn128_mul( const char* g1, uint32_t g1_len, const char* scalar, uint32_t scalar_len, char* result, uint32_t result_len);
   binary alt_bn128_mul(1:binary g1, 2:binary scalar),
   // int32_t alt_bn128_pair( const char* pairs, uint32_t pairs_len);
   i32 alt_bn128_pair(1:binary pairs),
   // int32_t mod_exp( const char* base, uint32_t base_len, const char* exp, uint32_t exp_len, const char* mod, uint32_t mod_len, char* result, uint32_t result_len);
   binary mod_exp(1:binary base, 2:binary exp, 3:binary mod),
}
