# cython: c_string_type=str, c_string_encoding=ascii

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
    ctypedef int          int32_t
    ctypedef unsigned short uint16_t
    ctypedef unsigned char uint8_t
    ctypedef int __uint128_t #hacking

cdef extern from "<Python.h>":
    ctypedef long long PyLongObject

    object PyBytes_FromStringAndSize(const char* str, int size)
    int _PyLong_AsByteArray(PyLongObject* v, unsigned char* bytes, size_t n, int little_endian, int is_signed)

cdef extern from "<uuos.hpp>":
    chain_proxy *chain(uint64_t ptr)
    void uuosext_init()

    ctypedef struct chain_proxy:
        void say_hello()

        void id(string& chain_id)
        void start_block(string& _time, uint16_t confirm_block_count, string& _new_features)
        int abort_block()
        bool startup(bool initdb)
        void finalize_block(string& _priv_keys)
        void commit_block()
        string get_block_id_for_num(uint32_t block_num)
        string get_global_properties()
        string get_dynamic_global_properties()
        string get_actor_whitelist()

        void set_actor_blacklist(string& params)
        void set_contract_whitelist(string& params)
        void set_action_blacklist(string& params)
        void set_key_blacklist(string& params)
        uint32_t head_block_num()
        string head_block_time()
        string head_block_id()
        string head_block_producer()
        string head_block_header()
        string head_block_state()
        uint32_t fork_db_head_block_num()
        string fork_db_head_block_id()
        string fork_db_head_block_time()
        string fork_db_head_block_producer()
        uint32_t fork_db_pending_head_block_num()
        string fork_db_pending_head_block_id()
        string fork_db_pending_head_block_time()
        string fork_db_pending_head_block_producer()
        string pending_block_time()
        string pending_block_producer()
        string pending_producer_block_id()
        string get_pending_trx_receipts()
        string active_producers()
        string pending_producers()
        string proposed_producers()
        uint32_t last_irreversible_block_num()
        string last_irreversible_block_id()
        string fetch_block_by_number(uint32_t block_num)
        string fetch_block_by_id(string& params)
        string fetch_block_state_by_number(uint32_t block_num)
        string fetch_block_state_by_id(string& params)
        string calculate_integrity_hash()
        bool sender_avoids_whitelist_blacklist_enforcement(string& sender)
        bool check_actor_list(string& param)
        bool check_contract_list(string& param)
        bool check_action_list(string& code, string& action)
        bool check_key_list(string& param)
        bool is_building_block()
        bool is_producing_block()
        bool is_ram_billing_in_notify_allowed()
        void add_resource_greylist(string& param)
        void remove_resource_greylist(string& param)
        bool is_resource_greylisted(string& param)
        string get_resource_greylist()
        string get_config()
        bool validate_expiration(string& param)
        bool validate_tapos(string& param)
        bool validate_db_available_size()
        bool validate_reversible_available_size()
        bool is_protocol_feature_activated(string& param)
        bool is_builtin_activated(int feature)
        bool is_known_unexpired_transaction(string& param)
        int64_t set_proposed_producers(string& param)
        bool light_validation_allowed()
        bool skip_auth_check()
        bool skip_db_sessions()
        bool skip_trx_checks()
        bool contracts_console()
        void get_chain_id(string& result)
        int get_read_mode()
        int get_validation_mode()
        void set_subjective_cpu_leeway(uint64_t leeway)
        void set_greylist_limit(uint32_t limit)
        uint32_t get_greylist_limit()
        void add_to_ram_correction(string& account, uint64_t ram_bytes, uint32_t action_id, const char* event_id)
        bool all_subjective_mitigations_disabled()
        string get_scheduled_producer(string& _block_time)

        void gen_transaction(string& _actions, string& expiration, string& reference_block_id, string& _chain_id, bool compress, string& _private_keys, vector[char]& result)
        string push_transaction(string& _packed_trx, string& deadline, uint32_t billed_cpu_time_us)

        string get_scheduled_transactions()
        string get_scheduled_transaction(__uint128_t sender_id, string& sender)
        string push_scheduled_transaction(string& scheduled_tx_id, string& deadline, uint32_t billed_cpu_time_us)

        bool pack_action_args(string& name, string& action, string& _args, vector[char]& result)
        string unpack_action_args(string& name, string& action, string& _binargs)
        string get_producer_public_keys()

        void clear_abi_cache(string& account)

        string& get_last_error()
        void set_last_error(string& error)

    ctypedef struct uuos_proxy:
        chain_proxy* chain_new(string& config, string& _genesis, string& protocol_features_dir, string& snapshot_dir)
        void chain_free(chain_proxy* api)

    uuos_proxy *get_uuos_proxy()


def chain_new(string& config, string& _genesis, string& protocol_features_dir, string& snapshot_dir):
    return <uint64_t>get_uuos_proxy().chain_new(config, _genesis, protocol_features_dir, snapshot_dir)

def chain_free(uint64_t ptr):
    get_uuos_proxy().chain_free(<chain_proxy*>ptr)

def chain_say_hello(uint64_t ptr):
    chain(ptr).say_hello()

def id(uint64_t ptr):
    cdef string chain_id
    chain(ptr).id(chain_id)
    return chain_id

def start_block(uint64_t ptr, string& _time, uint16_t confirm_block_count, string& _new_features):
    return chain(ptr).start_block(_time, confirm_block_count, _new_features)

def startup(uint64_t ptr, initdb):
    return chain(ptr).startup(initdb)

def abort_block(uint64_t ptr):
    return chain(ptr).abort_block()

def finalize_block(uint64_t ptr, string& _priv_keys):
    chain(ptr).finalize_block(_priv_keys)

def commit_block(uint64_t ptr):
    chain(ptr).commit_block()

def get_last_error(uint64_t ptr):
    cdef string error
    error = chain(ptr).get_last_error()

def set_last_error(uint64_t ptr, string& error):
    chain(ptr).set_last_error(error)

def get_block_id_for_num(uint64_t ptr, uint32_t block_num):
    return chain(ptr).get_block_id_for_num(block_num)

def get_global_properties(uint64_t ptr):
    return chain(ptr).get_global_properties()

def get_dynamic_global_properties(uint64_t ptr):
    return chain(ptr).get_dynamic_global_properties()

def get_actor_whitelist(uint64_t ptr):
    return chain(ptr).get_actor_whitelist()

def set_actor_blacklist(uint64_t ptr, string& params):
    return chain(ptr).get_actor_whitelist()

def set_contract_whitelist(uint64_t ptr, string& params):
    return chain(ptr).set_contract_whitelist(params)

def set_action_blacklist(uint64_t ptr, string& params):
    return chain(ptr).set_action_blacklist(params)

def set_key_blacklist(uint64_t ptr, string& params):
    return chain(ptr).set_key_blacklist(params)

def head_block_num(uint64_t ptr):
    '''
    returns: int
    '''
    return chain(ptr).head_block_num()

def head_block_time(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).head_block_time()

def head_block_id(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).head_block_id()

def head_block_producer(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).head_block_producer()

def head_block_header(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).head_block_header()

def head_block_state(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).head_block_state()

def fork_db_head_block_num(uint64_t ptr):
    '''
    returns: int
    '''
    return chain(ptr).fork_db_head_block_num()

def fork_db_head_block_id(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).fork_db_head_block_id()

def fork_db_head_block_time(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).fork_db_head_block_time()

def fork_db_head_block_producer(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).fork_db_head_block_producer()

def fork_db_pending_head_block_num(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).fork_db_pending_head_block_num()

def fork_db_pending_head_block_id(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).fork_db_pending_head_block_id()

def fork_db_pending_head_block_time(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).fork_db_pending_head_block_time()

def fork_db_pending_head_block_producer(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).fork_db_pending_head_block_producer()

def pending_block_time(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).pending_block_time()

def pending_block_producer(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).pending_block_producer()

def pending_producer_block_id(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).pending_producer_block_id()

def get_pending_trx_receipts(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).get_pending_trx_receipts()

def active_producers(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).active_producers()

def pending_producers(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).pending_producers()

def proposed_producers(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).proposed_producers()

def last_irreversible_block_num(uint64_t ptr):
    '''
    returns: int
    '''
    return chain(ptr).last_irreversible_block_num()

def last_irreversible_block_id(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).last_irreversible_block_id()

def fetch_block_by_number(uint64_t ptr, uint32_t block_num):
    '''
    returns: bytes
    '''
    return <bytes>chain(ptr).fetch_block_by_number(block_num)

def fetch_block_by_id(uint64_t ptr, string& params):
    '''
    returns: bytes
    '''
    return <bytes>chain(ptr).fetch_block_by_id(params)

def fetch_block_state_by_number(uint64_t ptr, uint32_t block_num):
    '''
    returns: bytes
    '''
    return <bytes>chain(ptr).fetch_block_state_by_number(block_num)

def fetch_block_state_by_id(uint64_t ptr, string& params):
    '''
    returns: bytes
    '''
    return <bytes>chain(ptr).fetch_block_state_by_id(params)

def calculate_integrity_hash(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).calculate_integrity_hash()

def sender_avoids_whitelist_blacklist_enforcement(uint64_t ptr, string& sender):
    '''
    returns: str
    '''
    return chain(ptr).sender_avoids_whitelist_blacklist_enforcement(sender)

def check_actor_list(uint64_t ptr, string& param):
    '''
    returns: str
    '''
    return chain(ptr).check_actor_list(param)

def check_contract_list(uint64_t ptr, string& param):
    '''
    returns: str
    '''
    return chain(ptr).check_contract_list(param)

def check_action_list(uint64_t ptr, string& code, string& action):
    '''
    returns: str
    '''
    return chain(ptr).check_action_list(code, action)

def check_key_list(uint64_t ptr, string& param):
    '''
    returns: str
    '''
    return chain(ptr).check_key_list(param)

def is_building_block(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).is_building_block()

def is_producing_block(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).is_producing_block()

def is_ram_billing_in_notify_allowed(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).is_ram_billing_in_notify_allowed()

def add_resource_greylist(uint64_t ptr, string& param):
    '''
    returns: str
    '''
    return chain(ptr).add_resource_greylist(param)

def remove_resource_greylist(uint64_t ptr, string& param):
    '''
    returns: str
    '''
    return chain(ptr).remove_resource_greylist(param)

def is_resource_greylisted(uint64_t ptr, string& param):
    '''
    returns: str
    '''
    return chain(ptr).is_resource_greylisted(param)

def get_resource_greylist(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).get_resource_greylist()

def get_config(uint64_t ptr):
    '''
    returns: str
    '''
    return chain(ptr).get_config()

def validate_expiration(uint64_t ptr, string& param):
    return chain(ptr).validate_expiration(param)

def validate_tapos(uint64_t ptr, string& param):
    return chain(ptr).validate_tapos(param)

def validate_db_available_size(uint64_t ptr):
    '''
    returns: bool
    '''
    return chain(ptr).validate_db_available_size()

def validate_reversible_available_size(uint64_t ptr):
    '''
    returns: bool
    '''
    return chain(ptr).validate_reversible_available_size()

def is_protocol_feature_activated(uint64_t ptr, string& param):
    '''
    returns: bool
    '''
    return chain(ptr).is_protocol_feature_activated(param)

def is_builtin_activated(uint64_t ptr, int feature):
    '''
    returns: bool
    '''
    return chain(ptr).is_builtin_activated(feature)

def is_known_unexpired_transaction(uint64_t ptr, string& param):
    '''
    returns: bool
    '''
    return chain(ptr).is_known_unexpired_transaction(param)

def set_proposed_producers(uint64_t ptr, string& param):
    '''
    returns: int version
    '''
    return chain(ptr).set_proposed_producers(param)

def light_validation_allowed(uint64_t ptr):
    '''
    returns: bool
    '''
    return chain(ptr).light_validation_allowed()

def skip_auth_check(uint64_t ptr):
    '''
    returns: bool
    '''
    return chain(ptr).skip_auth_check()

def skip_db_sessions(uint64_t ptr):
    '''
    returns: bool
    '''
    return chain(ptr).skip_db_sessions()

def skip_trx_checks(uint64_t ptr):
    '''
    returns: bool
    '''
    return chain(ptr).skip_trx_checks()

def contracts_console(uint64_t ptr):
    '''
    returns: bool
    '''
    return chain(ptr).contracts_console()

def get_read_mode(uint64_t ptr):
    '''
    returns: int
    '''
    return chain(ptr).get_read_mode()

def get_validation_mode(uint64_t ptr):
    '''
    returns: int
    '''
    return chain(ptr).get_validation_mode()

def set_subjective_cpu_leeway(uint64_t ptr, uint64_t leeway):
    return chain(ptr).set_subjective_cpu_leeway(leeway)

def set_greylist_limit(uint64_t ptr, uint32_t limit):
    return chain(ptr).set_greylist_limit(limit)

def get_greylist_limit(uint64_t ptr):
    '''
    returns: int
    '''
    return chain(ptr).get_greylist_limit()

def add_to_ram_correction(uint64_t ptr, string& account, uint64_t ram_bytes, uint32_t action_id, const char* event_id):
    return chain(ptr).add_to_ram_correction(account, ram_bytes, action_id, event_id)

def all_subjective_mitigations_disabled(uint64_t ptr):
    '''
    returns: bool
    '''
    return chain(ptr).all_subjective_mitigations_disabled()

def get_scheduled_producer(uint64_t ptr, string& block_time):
    '''
    returns: str
    '''
    return chain(ptr).get_scheduled_producer(block_time)

def gen_transaction(uint64_t ptr, string& _actions, string& expiration, string& reference_block_id, string& _chain_id, bool compress, string& _private_keys):
    cdef vector[char] result
    chain(ptr).gen_transaction(_actions, expiration, reference_block_id, _chain_id, compress, _private_keys, result)
    return PyBytes_FromStringAndSize(result.data(), result.size())

def push_transaction(uint64_t ptr, string& _packed_trx, string& deadline, uint32_t billed_cpu_time_us):
    return chain(ptr).push_transaction(_packed_trx, deadline, billed_cpu_time_us)

def get_scheduled_transactions(uint64_t ptr):
    return chain(ptr).get_scheduled_transactions()

def get_scheduled_transaction(uint64_t ptr, object _sender_id, string& sender):
    cdef string result
    cdef __uint128_t sender_id

    sender_id = 0
    _PyLong_AsByteArray(<PyLongObject *><void *>_sender_id, <unsigned char *>&sender_id, sizeof(__uint128_t), 1, 0);
    return chain(ptr).get_scheduled_transaction(sender_id, sender)

def push_scheduled_transaction(uint64_t ptr, string& scheduled_tx_id, string& deadline, uint32_t billed_cpu_time_us):
    return chain(ptr).push_scheduled_transaction(scheduled_tx_id, deadline, billed_cpu_time_us)

def pack_action_args(uint64_t ptr, string& name, string& action, string& _args):
    cdef vector[char] result
    chain(ptr).pack_action_args(name, action, _args, result)
    return PyBytes_FromStringAndSize(result.data(), result.size())

def unpack_action_args(uint64_t ptr, name, action, _binargs):
    return chain(ptr).unpack_action_args(name, action, _binargs)

def clear_abi_cache(uint64_t ptr, string& account):
    return chain(ptr).clear_abi_cache(account)

def get_producer_public_keys(uint64_t ptr):
    return chain(ptr).get_producer_public_keys()

