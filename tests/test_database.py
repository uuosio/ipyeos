import os
import sys
import json
import struct
import pytest
import time

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, '..'))

from ipyeos import eos, log
from ipyeos import chaintester
from ipyeos.chaintester import ChainTester
from ipyeos import database

chaintester.chain_config['contracts_console'] = True

logger = log.get_logger(__name__)

def update_auth(chain, account):
    a = {
        "account": account,
        "permission": "active",
        "parent": "owner",
        "auth": {
            "threshold": 1,
            "keys": [
                {
                    "key": 'EOS6AjF6hvF7GSuSd4sCgfPKq5uWaXvGM2aQtEUCwmEHygQaqxBSV',
                    "weight": 1
                }
            ],
            "accounts": [{"permission":{"actor":account,"permission": 'eosio.code'}, "weight":1}],
            "waits": []
        }
    }
    chain.push_action('eosio', 'updateauth', a, {account:'active'})

def init_chain(initialize=True):
    chain = chaintester.ChainTester(initialize)
    # update_auth(chain, 'hello')
    return chain

def chain_test(initialize=True):
    def init_call(fn):
        def call(*args, **vargs):
            chain = init_chain(initialize)
            ret = fn(chain, *args, **vargs)
            chain.free()
            return ret
        return call
    return init_call

class NewChain():
    def __init__(self):
        self.chain = None

    def __enter__(self):
        self.chain = init_chain()
        return self.chain

    def __exit__(self, type, value, traceback):
        self.chain.free()

def unpack_length(val: bytes):
    assert len(val) > 0, "raw VarUint32 value cannot be empty"
    v = 0
    by = 0
    n = 0
    for b in val:
        v |= (b & 0x7f) << by
        by += 7
        n += 1
        if b & 0x80 == 0:
            break
    return v, n

class Decoder(object):
    def __init__(self, raw_data: bytes):
        self.raw_data = raw_data
        self.pos = 0

    def read_bytes(self, size):
        assert len(self.raw_data) >= self.pos + size
        ret = self.raw_data[self.pos:self.pos+size]
        self.pos += size
        return ret

    def unpack_name(self):
        name = self.read_bytes(8)
        return eos.b2s(name)

    def unpack_u8(self):
        ret = self.read_bytes(1)[0]
        return ret

    def unpack_u16(self):
        ret = int.from_bytes(self.read_bytes(2), 'little')
        return ret

    def unpack_u32(self):
        ret = int.from_bytes(self.read_bytes(4), 'little')
        return ret

    def unpack_u64(self):
        ret = int.from_bytes(self.read_bytes(8), 'little')
        return ret

    def unpack_checksum256(self):
        ret = self.read_bytes(32)
        return ret

    def unpack_length(self):
        v = 0
        by = 0
        while True:
            b = self.unpack_u8()
            v |= (b & 0x7f) << by
            by += 7
            if b & 0x80 == 0:
                break
        return v

    def unpack_bytes(self):
        length = self.unpack_length()
        data = self.read_bytes(length)
        return data
    
    def unpack_time_point(self):
        return self.unpack_u64()

    def unpack_public_key(self):
        ret = self.read_bytes(33)
        return ret

    def get_bytes(self, size):
        ret = self.read_bytes(size)
        return ret

    def get_pos(self):
        return self.pos

test_dir = os.path.dirname(__file__)
def deploy_contract(tester, package_name):
    with open(f'{test_dir}/{package_name}.wasm', 'rb') as f:
        code = f.read()
    with open(f'{test_dir}/{package_name}.abi', 'rb') as f:
        abi = f.read()
    tester.deploy_contract('hello', code, abi)

@chain_test(True)
def test_walk(chain: ChainTester):
    def on_data(tp, id, raw_data):
        print(tp, len(raw_data))
        if tp == 1:
            print(eos.b2s(raw_data[8:16]))
        return 1
    object_types = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31, 32, 33, 34, 38, 39, 40, 41]
    for tp in object_types:
        if tp in [15, ]: #block_summary_object, code_object
            continue
        chain.db.walk(tp, 0, on_data)

@chain_test(True)
def test_row_count(chain: ChainTester):
    object_types = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31, 32, 33, 34, 38, 39, 40, 41]
    for tp in object_types:
        count = chain.db.row_count(tp)
        print(f'+++++++++{tp}: {count}')

@chain_test(True)
def test_2walk_range(chain: ChainTester):
    def on_data(tp, raw_data):
        print(tp, raw_data)
        if tp == 1:
            print(eos.b2s(raw_data[:8]))
        return 1
    object_types = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31, 32, 33, 34, 38, 39, 40, 41]

    for tp in object_types:
        if tp in [15, 40]: #block_summary_object, code_object
            continue
        chain.db.walk_range(tp, 0, on_data, int.to_bytes(0, 8, 'little'), int.to_bytes(10, 8, 'little'))

def parse_code(raw_data: bytes):
    print('+++++++raw_data:', len(raw_data))
    dec = Decoder(raw_data)
    table_id = dec.unpack_u64()

    code_hash = dec.unpack_checksum256()
    print('+++code hash:', code_hash)
    code = dec.unpack_bytes()
    code_ref_count = dec.unpack_u64()
    first_block_used = dec.unpack_u32()
    vm_type = dec.unpack_u8()
    vm_version = dec.unpack_u8()
    print(code_ref_count, first_block_used, vm_type, vm_version)
    print('len(code):', len(code))
    # with open('out.wasm', 'wb') as f:
    #     f.write(code)
    return code_hash

@chain_test(True)
def test_find(chain: ChainTester):
    object_types = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31, 32, 33, 34, 38, 39, 40, 41]

    for tp in object_types:
        if tp in [15, ]: #block_summary_object, code_object
            continue
        raw_data = chain.db.find(tp, 0, int.to_bytes(0, 8, 'little'))
        if raw_data:
            print(tp, len(raw_data))

    if 0:
        key = int.to_bytes(1, 8, 'little')
        print('++++key:', key)
        raw_data = chain.db.find(40, 0, key)
        code_hash = parse_code(raw_data)
        # digest_type  code_hash; //< code_hash should not be changed within a chainbase modifier lambda
        # shared_blob  code;
        # uint64_t     code_ref_count;
        # uint32_t     first_block_used;
        # uint8_t      vm_type = 0; //< vm_type should not be changed within a chainbase modifier lambda
        # uint8_t      vm_version = 0; //< vm_version should not be changed within a chainbase modifier lambda

        #find with by_code_hash
        raw_key = code_hash + int.to_bytes(0, 1, 'little') + int.to_bytes(0, 1, 'little')
        raw_data = chain.db.find(40, 1, raw_key)
        parse_code(raw_data)


@chain_test(True)
def test_lower_bound(chain: ChainTester):
    object_types = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 30, 31, 32, 33, 34, 38, 39, 40, 41]
    start = time.time()
    for tp in object_types:
        if tp in [15, ]: #block_summary_object, code_object
            continue
        raw_data = chain.db.lower_bound(tp, 0, int.to_bytes(0, 8, 'little'))
        if raw_data:
            print(tp, len(raw_data))

    raw_data = chain.db.lower_bound(40, 0, int.to_bytes(1, 8, 'little'))
    print(40, len(raw_data))

    raw_data = chain.db.upper_bound(40, 0, int.to_bytes(1, 8, 'little'))
    print(40, len(raw_data))

    raw_data = chain.db.lower_bound(40, 0, int.to_bytes(0, 8, 'little'))
    print(40, len(raw_data))

    raw_data = chain.db.upper_bound(40, 0, int.to_bytes(0, 8, 'little'))
    print(40, len(raw_data))
    
    print(time.time() - start)

def parse_account_object(data: bytes):
    #class account_object:
    #   account_name         name; //< name should not be changed within a chainbase modifier lambda
    #   block_timestamp_type creation_date;
    #   shared_blob          abi;

    # ordered_unique<tag<by_id>, member<account_object, account_object::id_type, &account_object::id>>,
    # ordered_unique<tag<by_name>, member<account_object, account_name, &account_object::name>>
    dec = Decoder(data)
    table_id = dec.unpack_u64()
    name = dec.unpack_name()
    creation_data = dec.unpack_u32()
    abi = dec.unpack_bytes()
    print(name, creation_data)
    abi = eos.unpack_native_object(12, abi)
    # print(abi)
    return name

@chain_test(True)
def test_account_index(chain: ChainTester):
    key = int.to_bytes(0, 8, 'little')
    data = chain.db.find(database.account_object_type, 0, key)
    name = parse_account_object(data)

    # by_name
    key = eos.s2b(name)
    data = chain.db.find(database.account_object_type, 1, key)
    parse_account_object(data)

def parse_account_metadata_object(data: bytes):
    dec = Decoder(data)
    # class account_metadata_object:
    #   account_name          name; //< name should not be changed within a chainbase modifier lambda
    #   uint64_t              recv_sequence = 0;
    #   uint64_t              auth_sequence = 0;
    #   uint64_t              code_sequence = 0;
    #   uint64_t              abi_sequence  = 0;
    #   digest_type           code_hash;
    #   time_point            last_code_update;
    #   uint32_t              flags = 0;
    #   uint8_t               vm_type = 0;
    #   uint8_t               vm_version = 0;
    # ordered_unique<tag<by_id>, member<account_metadata_object, account_metadata_object::id_type, &account_metadata_object::id>>,
    # ordered_unique<tag<by_name>, member<account_metadata_object, account_name, &account_metadata_object::name>>
    name = dec.unpack_name()

    table_id = dec.unpack_u64()

    recv_sequence = dec.unpack_u64()
    auth_sequence = dec.unpack_u64()
    code_sequence = dec.unpack_u64()
    abi_sequence  = dec.unpack_u64()
    code_hash = dec.unpack_checksum256()
    last_code_update = dec.unpack_u64()
    flags = dec.unpack_u32()
    vm_type = dec.unpack_u8()
    vm_version = dec.unpack_u8()
    return (
        name,
        recv_sequence,
        auth_sequence,
        code_sequence,
        abi_sequence ,
        code_hash,
        last_code_update,
        flags,
        vm_type,
        vm_version,
    )


@chain_test(True)
def test_account_metadata_index(chain: ChainTester):
    key = int.to_bytes(0, 8, 'little')
    data = chain.db.find(database.account_metadata_object_type, 0, key)
    ret = parse_account_metadata_object(data)

    name = ret[0]
    print(name)
    # by_name
    key = eos.s2b(name)
    data = chain.db.find(database.account_metadata_object_type, 1, key)
    ret2 = parse_account_metadata_object(data)
    assert ret == ret2
    print(ret)

def parse_permission_object(raw_data: bytes):
    #class permission_object:
    #   permission_usage_object::id_type  usage_id;
    #   id_type                           parent; ///< parent permission
    #   account_name                      owner; ///< the account this permission belongs to (should not be changed within a chainbase modifier lambda)
    #   permission_name                   name; ///< human-readable name for the permission (should not be changed within a chainbase modifier lambda)
    #   time_point                        last_updated; ///< the last time this authority was updated
    #   shared_authority                  auth; ///< authority required to execute this permission
    #       uint32_t                                   threshold = 0;
    #       shared_vector<shared_key_weight>           keys;
    #           shared_public_key key;
    #           weight_type       weight;
    #       shared_vector<permission_level_weight>     accounts;
    #           permission_level  permission;
    #           weight_type       weight;
    #       shared_vector<wait_weight>                 waits;
    #           uint32_t     wait_sec;
    #           weight_type  weight;
    dec = Decoder(raw_data)
    table_id = dec.unpack_u64()

    usage_id = dec.unpack_u64()
    parent = dec.unpack_u64()
    owner = dec.unpack_name()
    name = dec.unpack_name()
    last_updated = dec.unpack_time_point()
    threshold = dec.unpack_u32()

    pos = dec.get_pos()
    size = dec.unpack_length()
    print('++++key_weight size:', size)
    for i in range(size):
        pub = dec.unpack_public_key()
        weight = dec.unpack_u16()
        print('++++key_weight:', pub, weight)

    size = dec.unpack_length()
    print('+++++++permission_level_weight size:', size)
    for i in range(size):
        actor = dec.unpack_name()
        permission = dec.unpack_name()
        weight = dec.unpack_u16()
        print("+++++++permission_level_weight:", actor, permission, weight)

    wait_weight_size = dec.unpack_length()
    print('++++++wait_weight_size:', wait_weight_size)
    for i in range(wait_weight_size):
        wait_sec = dec.unpack_u32()
        weight =dec.unpack_u16()
        print(wait_sec, weight)

    return (
        usage_id,
        parent,
        owner,
        name,
        last_updated,
        threshold,
    )

@chain_test(True)
def test_permission_index(chain: ChainTester):
    def on_data(tp, raw_data):
        print(tp, len(raw_data))
        try:
            parse_permission_object(raw_data)
            return 1
        except Exception as e:
            logger.exception(e)
            return 0

    chain.db.walk(database.permission_object_type, 0, on_data)

    chain.db.walk(database.permission_object_type, 1, on_data)
    chain.db.walk(database.permission_object_type, 2, on_data)
    chain.db.walk(database.permission_object_type, 3, on_data)

    #  ordered_unique<tag<by_parent>,
    #        member<permission_object, permission_object::id_type, &permission_object::parent>,
    #        member<permission_object, permission_object::id_type, &permission_object::id>
    lower_bound = int.to_bytes(0, 8, 'little') + int.to_bytes(0, 8, 'little')
    upper_bound = int.to_bytes(40, 8, 'little') + int.to_bytes(40, 8, 'little')
    chain.db.walk_range(database.permission_object_type, 1, lower_bound, upper_bound, on_data)

    #  ordered_unique<tag<by_owner>,
    #        member<permission_object, account_name, &permission_object::owner>,
    #        member<permission_object, permission_name, &permission_object::name>
    lower_bound = int.to_bytes(0, 8, 'little') + int.to_bytes(0, 8, 'little')
    upper_bound = int.to_bytes(0xffffffffffffffff, 8, 'little') + int.to_bytes(0xffffffffffffffff, 8, 'little')
    chain.db.walk_range(database.permission_object_type, 2, lower_bound, upper_bound, on_data)

    #  ordered_unique<tag<by_name>,
    #        member<permission_object, permission_name, &permission_object::name>,
    #        member<permission_object, permission_object::id_type, &permission_object::id>
    lower_bound = int.to_bytes(0, 8, 'little') + int.to_bytes(0, 8, 'little')
    upper_bound = int.to_bytes(0xffffffffffffffff, 8, 'little') + int.to_bytes(40, 8, 'little')
    chain.db.walk_range(database.permission_object_type, 3, lower_bound, upper_bound, on_data)

def parse_permission_usage_object(raw_data: bytes):
    #class permission_usage_object:
    #   time_point        last_used;   ///< when this permission was last used
    dec = Decoder(raw_data)
    table_id = dec.unpack_u64()
    last_used = dec.unpack_time_point()
    print('last_used:', last_used)

@chain_test(True)
def test_permission_usage_index(chain: ChainTester):
    def on_data(tp, raw_data):
        print(tp, len(raw_data))
        try:
            parse_permission_usage_object(raw_data)
            return 1
        except Exception as e:
            logger.exception(e)
            return 0

    chain.db.walk(database.permission_usage_object_type, 0, on_data)

    lower_bound = int.to_bytes(0, 8, 'little')
    upper_bound = int.to_bytes(40, 8, 'little')
    chain.db.walk_range(database.permission_usage_object_type, 0, lower_bound, upper_bound, on_data)

def parse_permission_link_object(raw_data: bytes):
    #class permission_link_object:
    #   /// The account which is defining its permission requirements
    #   account_name    account;
    #   /// The contract which account requires @ref required_permission to invoke
    #   account_name    code; /// TODO: rename to scope
    #   /// The message type which account requires @ref required_permission to invoke
    #   /// May be empty; if so, it sets a default @ref required_permission for all messages to @ref code
    #   action_name       message_type;
    #   /// The permission level which @ref account requires for the specified message types
    #   /// all of the above fields should not be changed within a chainbase modifier lambda
    #   permission_name required_permission;
    dec = Decoder(raw_data)
    table_id = dec.unpack_u64()
    account = dec.unpack_name()
    code = dec.unpack_name()
    message_type = dec.unpack_name()
    required_permission = dec.unpack_name()
    print(account, code, message_type, required_permission)

@chain_test(True)
def test_permission_link_index(chain: ChainTester):
    def on_data(tp, raw_data):
        print(tp, len(raw_data))
        try:
            parse_permission_link_object(raw_data)
            return 1
        except Exception as e:
            logger.exception(e)
            return 0
    count = chain.db.row_count(database.permission_link_object_type)
    print('+++++++row count:', count)
    chain.db.walk(database.permission_link_object_type, 0, on_data)
    return

    # ordered_unique<tag<by_action_name>,
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, account_name, account),
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, account_name, code),
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, action_name, message_type)
    # ordered_unique<tag<by_permission_name>,
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, account_name, account),
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, permission_name, required_permission),
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, permission_link_object::id_type, id)
    lower_bound = int.to_bytes(0, 8, 'little')
    upper_bound = int.to_bytes(40, 8, 'little')
    chain.db.walk_range(database.permission_link_object_type, 0, lower_bound, upper_bound, on_data)

@chain_test(True)
def test_contract_table_objects(tester: ChainTester):
    # class table_id_object : public chainbase::object<table_id_object_type, table_id_object> {
    #     id_type        id;
    #     account_name   code;  //< code should not be changed within a chainbase modifier lambda
    #     scope_name     scope; //< scope should not be changed within a chainbase modifier lambda
    #     table_name     table; //< table should not be changed within a chainbase modifier lambda
    #     account_name   payer;
    #     uint32_t       count = 0; /// the number of elements in the table
    # };
    #         ordered_unique<tag<by_code_scope_table>,
    #             member<table_id_object, account_name, &table_id_object::code>,
    #             member<table_id_object, scope_name,   &table_id_object::scope>,
    #             member<table_id_object, table_name,   &table_id_object::table>

    #struct key_value_object
    #   id_type               id;
    #   table_id              t_id; //< t_id should not be changed within a chainbase modifier lambda
    #   uint64_t              primary_key; //< primary_key should not be changed within a chainbase modifier lambda
    #   account_name          payer;
    #   shared_blob           value;
    # ordered_unique<tag<by_scope_primary>,
    #     member<key_value_object, table_id, &key_value_object::t_id>,
    #     member<key_value_object, uint64_t, &key_value_object::primary_key>

    count = tester.db.row_count(database.key_value_object_type)
    count2 = tester.db.row_count(database.table_id_object_type)
    print(count, count2)

    def parse_table_id_object_data(raw_data):
        # print(tp, len(raw_data))
        dec = Decoder(raw_data)
        table_id = dec.unpack_u64()
        code = dec.unpack_name()
        scope = dec.unpack_name()
        table = dec.unpack_name()
        payer = dec.unpack_name()
        count = dec.unpack_u32()
        return (table_id, code, scope, table, payer, count)

    def on_table_id_object_data(tp, raw_data):
        ret = parse_table_id_object_data(raw_data)
        print(ret)
        return 1

    print('++++++++++walk+++++++++')
    tester.db.walk(database.table_id_object_type, 0, on_table_id_object_data)
    print('++++++++++walk_range+++++++++')
    lower_bound = eos.s2b('eosio.token') + eos.s2b("") + eos.s2b("")
    upper_bound = eos.s2b('eosio.token') + eos.s2b("zzzzzzzzzzzzj") + eos.s2b("zzzzzzzzzzzzj")
    tester.db.walk_range(database.table_id_object_type, 1, lower_bound, upper_bound, on_table_id_object_data)

#    struct secondary_index
#          table_id      t_id; //< t_id should not be changed within a chainbase modifier lambda
#          uint64_t      primary_key; //< primary_key should not be changed within a chainbase modifier lambda
#          account_name  payer;
#          SecondaryKey  secondary_key; //< secondary_key should not be changed within a chainbase modifier lambda

#             ordered_unique<tag<by_id>, member<index_object, typename index_object::id_type, &index_object::id>>,
#             ordered_unique<tag<by_primary>,
#                   member<index_object, table_id, &index_object::t_id>,
#                   member<index_object, uint64_t, &index_object::primary_key>
#             ordered_unique<tag<by_secondary>,
#                   member<index_object, table_id, &index_object::t_id>,
#                   member<index_object, SecondaryKey, &index_object::secondary_key>,
#                   member<index_object, uint64_t, &index_object::primary_key>

    def parse_key_value_object(raw_data):
        dec = Decoder(raw_data)
    #   table_id              t_id; //< t_id should not be changed within a chainbase modifier lambda
    #   uint64_t              primary_key; //< primary_key should not be changed within a chainbase modifier lambda
    #   account_name          payer;
    #   shared_blob           value;
        table_id = dec.unpack_u64()
        t_id = dec.unpack_u64()
        primary_key = dec.unpack_u64()
        payer = dec.unpack_name()
        value = dec.unpack_bytes()
        return (table_id, t_id, primary_key, payer, value)

    def on_data_key_value(tp, raw_data):
        # print(tp, len(raw_data))
        assert tp == database.key_value_object_type
        ret = parse_key_value_object(raw_data)
        print(ret)
        return 1

    def on_data_secondary(tp, raw_data):
        print(tp, len(raw_data))
        dec = Decoder(raw_data)
        table_id = dec.unpack_u64()
        # t_id = dec.unpack_u64()
        primary_key = dec.unpack_u64()
        payer = dec.unpack_name()
        value = raw_data[dec.get_pos():]
        print(primary_key, payer, value)
        return 1

    deploy_contract(tester, 'test')

    args = {
        'key': 1,
        'hash': '0000000000000000000000000000000100000000000000000000000000000000'
    }
    r = tester.push_action('hello', 'teststore', args, {'hello': 'active'})

    lower_bound = int.to_bytes(0, 8, 'little')
    upper_bound = int.to_bytes(0x7fffffffffffffff, 8, 'little')
    logger.info('++++++++++walk key_value+++++++++')
    tester.db.walk_range(database.key_value_object_type, 0, lower_bound, upper_bound, on_data_key_value)

    logger.info('++++++++++walk index64+++++++++')
    tester.db.walk_range(database.index64_object_type, 0, lower_bound, upper_bound, on_data_secondary)

    logger.info('++++++++++walk index128+++++++++')
    tester.db.walk_range(database.index128_object_type, 0, lower_bound, upper_bound, on_data_secondary)

    logger.info('++++++++++walk index256+++++++++')
    tester.db.walk_range(database.index256_object_type, 0, lower_bound, upper_bound, on_data_secondary)

    logger.info('++++++++++walk index double+++++++++')
    tester.db.walk_range(database.index_double_object_type, 0, lower_bound, upper_bound, on_data_secondary)

    logger.info('++++++++++walk index long double+++++++++')
    tester.db.walk_range(database.index_long_double_object_type, 0, lower_bound, upper_bound, on_data_secondary)

    logger.info('++++++++++walk range hello+++++++++')
    #         ordered_unique<tag<by_code_scope_table>,
    #             member<table_id_object, account_name, &table_id_object::code>,
    #             member<table_id_object, scope_name,   &table_id_object::scope>,
    #             member<table_id_object, table_name,   &table_id_object::table>
    lower_bound = eos.s2b('hello') + eos.s2b("") + eos.s2b("")
    upper_bound = eos.s2b('hello') + eos.s2b("zzzzzzzzzzzzj") + eos.s2b("zzzzzzzzzzzzj")
    logger.info('++++++table_id_object count: %s', tester.db.row_count(database.table_id_object_type))
    tester.db.walk_range(database.table_id_object_type, 1, lower_bound, upper_bound, on_table_id_object_data)

    raw_data = tester.db.lower_bound(database.table_id_object_type, 1, lower_bound)
    logger.info(raw_data)
    ret = parse_table_id_object_data(raw_data)
    table_id = ret[0]
    logger.info(ret)

    lower_bound = int.to_bytes(table_id, 8, 'little') + int.to_bytes(0, 8, 'little')
    raw_data = tester.db.lower_bound(database.key_value_object_type, 1, lower_bound)
    ret = parse_key_value_object(raw_data)
    logger.info(ret)

@chain_test(True)
def test_find_all_table_in_contract(tester: ChainTester):
    def parse_table_id_object_data(raw_data):
        # print(tp, len(raw_data))
        dec = Decoder(raw_data)
        table_id = dec.unpack_u64()
        code = dec.unpack_name()
        scope = dec.unpack_name()
        table = dec.unpack_name()
        payer = dec.unpack_name()
        count = dec.unpack_u32()
        return (table_id, code, scope, table, payer, count)

    def parse_secondary_data(raw_data):
        dec = Decoder(raw_data)
        table_id = dec.unpack_u64()
        t_id = dec.unpack_u64()
        primary_key = dec.unpack_u64()
        payer = dec.unpack_name()
        value = raw_data[dec.get_pos():]
        return(table_id, t_id, primary_key, payer, value)

    def on_table_id_object_data(tp, raw_data):
        ret = parse_table_id_object_data(raw_data)
        logger.info(ret)
        table_id = ret[0]

        lower_bound = int.to_bytes(table_id, 8, 'little') + int.to_bytes(0, 8, 'little')
        raw_data = tester.db.lower_bound(database.key_value_object_type, 1, lower_bound)
        if raw_data:
            ret = parse_key_value_object(raw_data)
            t_id = ret[1]
            if t_id == table_id:
                logger.info(ret)

        secondary_types = [
            database.index64_object_type,
            database.index128_object_type,
            database.index256_object_type,
            database.index_double_object_type,
            database.index_long_double_object_type
        ]

        secondary_types_map = {
            database.index64_object_type: "index64",
            database.index128_object_type: "index128",
            database.index256_object_type: "index256",
            database.index_double_object_type: "index_double",
            database.index_long_double_object_type: "index_long_double"
        }

        for secondary_type in secondary_types:
            raw_data = tester.db.lower_bound(secondary_type, 1, lower_bound)
            if raw_data:
                ret = parse_secondary_data(raw_data)
                t_id = ret[1]
                if t_id == table_id:
                    logger.info("+++%s %s", secondary_types_map[secondary_type], ret)
                    break
        return 1

    def parse_key_value_object(raw_data):
        dec = Decoder(raw_data)
    #   table_id              t_id; //< t_id should not be changed within a chainbase modifier lambda
    #   uint64_t              primary_key; //< primary_key should not be changed within a chainbase modifier lambda
    #   account_name          payer;
    #   shared_blob           value;
        table_id = dec.unpack_u64()
        t_id = dec.unpack_u64()
        primary_key = dec.unpack_u64()
        payer = dec.unpack_name()
        value = dec.unpack_bytes()
        return (table_id, t_id, primary_key, payer, value)

    def on_data_key_value(tp, raw_data):
        # print(tp, len(raw_data))
        assert tp == database.key_value_object_type
        ret = parse_key_value_object(raw_data)
        print(ret)
        return 1

    deploy_contract(tester, 'test')

    args = {
        'key': 1,
        'hash': '0000000000000000000000000000000100000000000000000000000000000000'
    }
    r = tester.push_action('hello', 'teststore', args, {'hello': 'active'})

    count = tester.db.row_count(database.key_value_object_type)
    count2 = tester.db.row_count(database.table_id_object_type)
    print(count, count2)

    print('++++++++++walk+++++++++')
    tester.db.walk(database.table_id_object_type, 0, on_table_id_object_data)
    print('++++++++++walk_range+++++++++')
    lower_bound = eos.s2b('hello') + eos.s2b("") + eos.s2b("")
    upper_bound = eos.s2b('hello') + eos.s2b("zzzzzzzzzzzzj") + eos.s2b("zzzzzzzzzzzzj")
    tester.db.walk_range(database.table_id_object_type, 1, lower_bound, upper_bound, on_table_id_object_data)
