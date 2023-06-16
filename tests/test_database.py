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

    def unpack_i64(self):
        ret = int.from_bytes(self.read_bytes(8), 'little', signed=True)
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
    
    def unpack_string(self):
        length = self.unpack_length()
        data = self.read_bytes(length)
        return data.decode()

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
    def on_data(tp, raw_data):
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
        chain.db.walk_range(tp, 0, int.to_bytes(0, 8, 'little'), int.to_bytes(10, 8, 'little'), on_data)

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
    table_id = dec.unpack_u64()
    name = dec.unpack_name()

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
    data = chain.db.find(database.account_metadata_object_type, 0, 0)
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

    # ordered_unique<tag<by_action_name>,
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, account_name, account),
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, account_name, code),
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, action_name, message_type)
    # ordered_unique<tag<by_permission_name>,
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, account_name, account),
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, permission_name, required_permission),
    #     BOOST_MULTI_INDEX_MEMBER(permission_link_object, permission_link_object::id_type, id)
    lower_bound = eos.s2b('') + eos.s2b('') + eos.s2b('')
    upper_bound = eos.s2b('hello') + eos.s2b('zzzzzzzzzzzzj') + eos.s2b('zzzzzzzzzzzzj')
    chain.db.walk_range(database.permission_link_object_type, 1, lower_bound, upper_bound, on_data)

    chain.db.walk_range(database.permission_link_object_type, 2, lower_bound, upper_bound, on_data)


    ret = chain.db.lower_bound(database.permission_link_object_type, 0, lower_bound)
    print(ret)
    ret = chain.db.lower_bound(database.permission_link_object_type, 1, lower_bound)
    print(ret)
    ret = chain.db.lower_bound(database.permission_link_object_type, 2, lower_bound)
    print(ret)

    ret = chain.db.upper_bound(database.permission_link_object_type, 0, lower_bound)
    print(ret)
    ret = chain.db.upper_bound(database.permission_link_object_type, 1, lower_bound)
    print(ret)
    ret = chain.db.upper_bound(database.permission_link_object_type, 2, lower_bound)
    print(ret)

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

@chain_test(True)
def test_global_property_object(tester: ChainTester):
    def on_global_property_object_data(tp, data):
        print(data)
        obj = eos.unpack_native_object(14, data)
        print(json.loads(obj))
        return 1

    tester.db.walk(database.global_property_object_type, 0, on_global_property_object_data)
    data = tester.db.find(database.global_property_object_type, 0, int.to_bytes(0, 8, 'little'))
    print(eos.unpack_native_object(14, data))

@chain_test(True)
def test_dynamic_global_property_object(tester: ChainTester):
#    class dynamic_global_property_object : public chainbase::object<dynamic_global_property_object_type, dynamic_global_property_object>
#         id_type    id;
#         uint64_t   global_action_sequence = 0;
    def on_dynamic_global_property_object(tp, data):
        print(data)
        dec = Decoder(data)
        table_id = dec.unpack_u64()
        global_action_sequence = dec.unpack_u64()
        print(table_id, global_action_sequence)
        return 1

    tester.db.walk(database.dynamic_global_property_object_type, 0, on_dynamic_global_property_object)
    data = tester.db.find(database.dynamic_global_property_object_type, 0, int.to_bytes(0, 8, 'little'))
    print(data)


@chain_test(True)
def test_block_summary_object(tester: ChainTester):
#    class block_summary_object : public chainbase::object<block_summary_object_type, block_summary_object>
#    {
#          id_type        id;
#          block_id_type  block_id;
    def on_block_summary_object(tp, data):
        # print(data)
        dec = Decoder(data)
        table_id = dec.unpack_u64()
        block_id = dec.unpack_checksum256()
        #print(table_id, block_id)
        return 1

    count = tester.db.row_count(database.block_summary_object_type)
    print(count)

    tester.db.walk(database.block_summary_object_type, 0, on_block_summary_object)
    data = tester.db.find(database.block_summary_object_type, 0, int.to_bytes(0, 8, 'little'))
    print(data)

@chain_test(True)
def test_transaction_object(tester: ChainTester):
#    class transaction_object : public chainbase::object<transaction_object_type, transaction_object>
#    {
#          OBJECT_CTOR(transaction_object)

#          id_type             id;
#          time_point_sec      expiration;
#          transaction_id_type trx_id; //< trx_id should not be changed within a chainbase modifier lambda
#    };

#    struct by_expiration;
#    struct by_trx_id;
#    using transaction_multi_index = chainbase::shared_multi_index_container<
#       transaction_object,
#       indexed_by<
#          ordered_unique< tag<by_id>, BOOST_MULTI_INDEX_MEMBER(transaction_object, transaction_object::id_type, id)>,
#          ordered_unique< tag<by_trx_id>, BOOST_MULTI_INDEX_MEMBER(transaction_object, transaction_id_type, trx_id)>,
#          ordered_unique< tag<by_expiration>,
#                BOOST_MULTI_INDEX_MEMBER( transaction_object, time_point_sec, expiration ),
#                BOOST_MULTI_INDEX_MEMBER( transaction_object, transaction_object::id_type, id)

    def parse_transaction_object(data):
        dec = Decoder(data)
        table_id = dec.unpack_u64()
        expiration = dec.unpack_u32()
        trx_id = dec.unpack_checksum256()
        return (table_id, expiration, trx_id)

    def on_transaction_object(tp, data):
        assert tp == database.transaction_object_type
        ret = parse_transaction_object(data)
        print(ret)
        return 1

    tester.produce_block()
    count = tester.db.row_count(database.transaction_object_type)
    print(count)

    tester.db.walk(database.transaction_object_type, 0, on_transaction_object)
    tester.db.walk(database.transaction_object_type, 1, on_transaction_object)
    tester.db.walk(database.transaction_object_type, 2, on_transaction_object)

    lower_bound = int.to_bytes(0, 8, 'little')
    upper_bound = int.to_bytes(0x7fffffffffffffff, 8, 'little')
    tester.db.walk_range(database.transaction_object_type, 0, lower_bound, upper_bound, on_transaction_object)

    lower_bound = int.to_bytes(0, 32, 'little')
    upper_bound = b'\xff'*32
    tester.db.walk_range(database.transaction_object_type, 1, lower_bound, upper_bound, on_transaction_object)

    lower_bound = b'\x00'*12
    upper_bound = b'\xff'*12
    tester.db.walk(database.transaction_object_type, 2, on_transaction_object)

    lower_bound = b'\x00'*32
    data = tester.db.lower_bound(database.transaction_object_type, 0, lower_bound)
    print(data)
    data = tester.db.lower_bound(database.transaction_object_type, 1, lower_bound)
    print(data)
    data = tester.db.lower_bound(database.transaction_object_type, 2, lower_bound)
    print(data)

    data = tester.db.upper_bound(database.transaction_object_type, 0, lower_bound)
    print(data)
    data = tester.db.upper_bound(database.transaction_object_type, 1, lower_bound)
    print(data)
    data = tester.db.upper_bound(database.transaction_object_type, 2, lower_bound)
    print(data)


    data1 = tester.db.find(database.transaction_object_type, 0, int.to_bytes(0, 8, 'little'))
    table_id, expiration, trx_id = parse_transaction_object(data1)
    print(table_id, expiration, trx_id)

    data2 = tester.db.find(database.transaction_object_type, 1, trx_id)
    print(data2)
    assert data1 == data2
    data3 = tester.db.find(database.transaction_object_type, 2, int.to_bytes(expiration, 4, 'little') + int.to_bytes(table_id, 8, 'little'))
    print(data3)
    assert data1 == data3


@chain_test(True)
def test_generated_transaction_object(tester: ChainTester):
#    class generated_transaction_object : public chainbase::object<generated_transaction_object_type, generated_transaction_object>
#          id_type                       id;
#          transaction_id_type           trx_id; //< trx_id should not be changed within a chainbase modifier lambda
#          account_name                  sender; //< sender should not be changed within a chainbase modifier lambda
#          uint128_t                     sender_id = 0; /// ID given this transaction by the sender (should not be changed within a chainbase modifier lambda)
#          account_name                  payer;
#          time_point                    delay_until; /// this generated transaction will not be applied until the specified time
#          time_point                    expiration; /// this generated transaction will not be applied after this time
#          time_point                    published;
#          shared_blob                   packed_trx;

#    struct by_trx_id;
#    struct by_expiration;
#    struct by_delay;
#    struct by_status;
#    struct by_sender_id;

#    using generated_transaction_multi_index = chainbase::shared_multi_index_container<
#       generated_transaction_object,
#       indexed_by<
#          ordered_unique< tag<by_id>, BOOST_MULTI_INDEX_MEMBER(generated_transaction_object, generated_transaction_object::id_type, id)>,
#          ordered_unique< tag<by_trx_id>, BOOST_MULTI_INDEX_MEMBER( generated_transaction_object, transaction_id_type, trx_id)>,
#          ordered_unique< tag<by_expiration>,
#                BOOST_MULTI_INDEX_MEMBER( generated_transaction_object, time_point, expiration),
#                BOOST_MULTI_INDEX_MEMBER( generated_transaction_object, generated_transaction_object::id_type, id)
#          ordered_unique< tag<by_delay>,
#                BOOST_MULTI_INDEX_MEMBER( generated_transaction_object, time_point, delay_until),
#                BOOST_MULTI_INDEX_MEMBER( generated_transaction_object, generated_transaction_object::id_type, id)
#          ordered_unique< tag<by_sender_id>,
#                BOOST_MULTI_INDEX_MEMBER( generated_transaction_object, account_name, sender),
#                BOOST_MULTI_INDEX_MEMBER( generated_transaction_object, uint128_t, sender_id)
    def parse_generated_transaction_object(data):
        dec = Decoder(data)
        table_id = dec.unpack_u64()
        trx_id = dec.unpack_checksum256()
        return (table_id, trx_id)

    def on_generated_transaction_object(tp, data):
        assert tp == database.generated_transaction_object_type
        ret = parse_generated_transaction_object(data)
        print(ret)
        return 1

    tester.produce_block()
    count = tester.db.row_count(database.generated_transaction_object_type)
    print(count)

    tester.db.walk(database.generated_transaction_object_type, 0, on_generated_transaction_object)
    tester.db.walk(database.generated_transaction_object_type, 1, on_generated_transaction_object)
    tester.db.walk(database.generated_transaction_object_type, 2, on_generated_transaction_object)
    tester.db.walk(database.generated_transaction_object_type, 3, on_generated_transaction_object)
    tester.db.walk(database.generated_transaction_object_type, 4, on_generated_transaction_object)

    lower_bound = int.to_bytes(0, 8, 'little')
    upper_bound = int.to_bytes(0x7fffffffffffffff, 8, 'little')
    tester.db.walk_range(database.generated_transaction_object_type, 0, lower_bound, upper_bound, on_generated_transaction_object)

    lower_bound = int.to_bytes(0, 32, 'little')
    upper_bound = b'\xff'*32
    tester.db.walk_range(database.generated_transaction_object_type, 1, lower_bound, upper_bound, on_generated_transaction_object)

    lower_bound = b'\x00'*12
    upper_bound = b'\xff'*12
    tester.db.walk(database.generated_transaction_object_type, 2, on_generated_transaction_object)

    lower_bound = b'\x00'*64
    upper_bound = b'\xff'*64
    tester.db.walk(database.generated_transaction_object_type, 3, on_generated_transaction_object)

    lower_bound = b'\x00'*64
    upper_bound = b'\xff'*64
    tester.db.walk(database.generated_transaction_object_type, 4, on_generated_transaction_object)

    lower_bound = b'\x00'*64
    data = tester.db.lower_bound(database.generated_transaction_object_type, 0, lower_bound)
    print(data)
    data = tester.db.lower_bound(database.generated_transaction_object_type, 1, lower_bound)
    print(data)
    data = tester.db.lower_bound(database.generated_transaction_object_type, 2, lower_bound)
    print(data)
    data = tester.db.lower_bound(database.generated_transaction_object_type, 3, lower_bound)
    print(data)
    data = tester.db.lower_bound(database.generated_transaction_object_type, 4, lower_bound)
    print(data)


    data = tester.db.upper_bound(database.generated_transaction_object_type, 0, lower_bound)
    print(data)
    data = tester.db.upper_bound(database.generated_transaction_object_type, 1, lower_bound)
    print(data)
    data = tester.db.upper_bound(database.generated_transaction_object_type, 2, lower_bound)
    print(data)
    data = tester.db.upper_bound(database.generated_transaction_object_type, 3, lower_bound)
    print(data)
    data = tester.db.upper_bound(database.generated_transaction_object_type, 4, lower_bound)
    print(data)


    data1 = tester.db.find(database.generated_transaction_object_type, 0, int.to_bytes(0, 8, 'little'))
    if data1:
        table_id, trx_id = parse_generated_transaction_object(data1)
        print(table_id, expiration, trx_id)

        data2 = tester.db.find(database.generated_transaction_object_type, 1, trx_id)
        if data2:
            print(data2)
            assert data1 == data2
    # data3 = tester.db.find(database.generated_transaction_object_type, 2, int.to_bytes(expiration, 4, 'little') + int.to_bytes(table_id, 8, 'little'))
    # print(data3)
    # assert data1 == data3

@chain_test(True)
def test_resource_limits_object(tester: ChainTester):
#    struct resource_limits_object : public chainbase::object<resource_limits_object_type, resource_limits_object> {
#       OBJECT_CTOR(resource_limits_object)
#       id_type id;
#       account_name owner; //< owner should not be changed within a chainbase modifier lambda
#       bool pending = false; //< pending should not be changed within a chainbase modifier lambda
#       int64_t net_weight = -1;
#       int64_t cpu_weight = -1;
#       int64_t ram_bytes = -1;
#    };

#    struct by_owner;
#    struct by_dirty;

#    using resource_limits_index = chainbase::shared_multi_index_container<
#       resource_limits_object,
#       indexed_by<
#          ordered_unique<tag<by_id>, member<resource_limits_object, resource_limits_object::id_type, &resource_limits_object::id>>,
#          ordered_unique<tag<by_owner>,
#                BOOST_MULTI_INDEX_MEMBER(resource_limits_object, bool, pending),
#                BOOST_MULTI_INDEX_MEMBER(resource_limits_object, account_name, owner)
    def parse_resource_limits_object(data):
        dec = Decoder(data)
        table_id = dec.unpack_u64()
        owner = dec.unpack_name()
        # pending = dec.unpack_u8()
        net_weight = dec.unpack_i64()
        cpu_weight = dec.unpack_i64()
        ram_bytes = dec.unpack_i64()
        return (
            table_id,
            owner,
            # pending,
            net_weight,
            cpu_weight,
            ram_bytes,
        )

    def on_resource_limits_object(tp, data):
        assert tp == database.resource_limits_object_type
        ret = parse_resource_limits_object(data)
        print(ret)
        return 1

    tester.produce_block()
    count = tester.db.row_count(database.resource_limits_object_type)
    print(count)

    tester.db.walk(database.resource_limits_object_type, 0, on_resource_limits_object)
    tester.db.walk(database.resource_limits_object_type, 1, on_resource_limits_object)

    lower_bound = int.to_bytes(0, 8, 'little')
    upper_bound = int.to_bytes(0x7fffffffffffffff, 8, 'little')
    tester.db.walk_range(database.resource_limits_object_type, 0, lower_bound, upper_bound, on_resource_limits_object)

    lower_bound = int.to_bytes(0, 32, 'little')
    upper_bound = b'\x00' + b'\xff'*31
    tester.db.walk_range(database.resource_limits_object_type, 1, lower_bound, upper_bound, on_resource_limits_object)

    data = tester.db.upper_bound(database.resource_limits_object_type, 0, lower_bound)
    print(data)
    data = tester.db.upper_bound(database.resource_limits_object_type, 1, lower_bound)
    print(data)

    data1 = tester.db.find(database.resource_limits_object_type, 0, int.to_bytes(0, 8, 'little'))
    ret = parse_resource_limits_object(data1)
    print(ret)

    # data2 = tester.db.find(database.resource_limits_object_type, 1, trx_id)
    # print(data2)
    # assert data1 == data2

class UsageAccumulator(object):
    def __init__(self, last_ordinal, value_ex, consumed):
        self.last_ordinal = last_ordinal
        self.value_ex = value_ex
        self.consumed = consumed

    @classmethod
    def unpack(cls, dec: Decoder):
        last_ordinal = dec.unpack_u32()
        value_ex = dec.unpack_u64()
        consumed = dec.unpack_u64()
        return UsageAccumulator(last_ordinal, value_ex, consumed)

    def __repr__(self):
        return str((self.last_ordinal, self.value_ex, self.consumed))

@chain_test(True)
def test_resource_usage_object(tester: ChainTester):
#    struct resource_usage_object : public chainbase::object<resource_usage_object_type, resource_usage_object> {
#       id_type id;
#       account_name owner; //< owner should not be changed within a chainbase modifier lambda
#       usage_accumulator        net_usage;
#       usage_accumulator        cpu_usage;
#       uint64_t                 ram_usage = 0;
#    };

#   struct exponential_moving_average_accumulator
#      uint32_t   last_ordinal;  ///< The ordinal of the last period which has contributed to the average
#      uint64_t   value_ex;      ///< The current average pre-multiplied by Precision
#      uint64_t   consumed;       ///< The last periods average + the current periods contribution so far

#    using resource_usage_index = chainbase::shared_multi_index_container<
#       resource_usage_object,
#       indexed_by<
#          ordered_unique<tag<by_id>, member<resource_usage_object, resource_usage_object::id_type, &resource_usage_object::id>>,
#          ordered_unique<tag<by_owner>, member<resource_usage_object, account_name, &resource_usage_object::owner> >
#       >
#    >;

    def parse_resource_usage_object(data):
        dec = Decoder(data)
        table_id = dec.unpack_u64()
        owner = dec.unpack_name()
        net_usage = UsageAccumulator.unpack(dec)
        cpu_usage = UsageAccumulator.unpack(dec)
        ram_usage = dec.unpack_u64()
        return (
            table_id,
            owner,
            net_usage,
            cpu_usage,
            ram_usage,
        )

    def on_resource_usage_object(tp, data):
        assert tp == database.resource_usage_object_type
        ret = parse_resource_usage_object(data)
        print(ret)
        return 1

    tester.produce_block()
    count = tester.db.row_count(database.resource_usage_object_type)
    print(count)

    tester.db.walk(database.resource_usage_object_type, 0, on_resource_usage_object)
    tester.db.walk(database.resource_usage_object_type, 1, on_resource_usage_object)

    lower_bound = int.to_bytes(0, 8, 'little')
    upper_bound = int.to_bytes(0x7fffffffffffffff, 8, 'little')
    tester.db.walk_range(database.resource_usage_object_type, 0, lower_bound, upper_bound, on_resource_usage_object)

    lower_bound = int.to_bytes(0, 8, 'little')
    upper_bound = b'\xff'*8
    tester.db.walk_range(database.resource_usage_object_type, 1, lower_bound, upper_bound, on_resource_usage_object)

    data = tester.db.upper_bound(database.resource_usage_object_type, 0, lower_bound)
    print(data)
    data = tester.db.upper_bound(database.resource_usage_object_type, 1, lower_bound)
    print(data)

    data1 = tester.db.find(database.resource_usage_object_type, 0, int.to_bytes(0, 8, 'little'))
    ret = parse_resource_usage_object(data1)
    print(ret)

    data1 = tester.db.find(database.resource_usage_object_type, 1, eos.s2b('hello'))
    ret = parse_resource_usage_object(data1)
    print(ret)



#    class resource_limits_state_object : public chainbase::object<resource_limits_state_object_type, resource_limits_state_object> {
#       OBJECT_CTOR(resource_limits_state_object);
#       id_type id;

#       /**
#        * Track the average netusage for blocks
#        */
#       usage_accumulator average_block_net_usage;

#       /**
#        * Track the average cpu usage for blocks
#        */
#       usage_accumulator average_block_cpu_usage;

#       void update_virtual_net_limit( const resource_limits_config_object& cfg );
#       void update_virtual_cpu_limit( const resource_limits_config_object& cfg );

#       uint64_t pending_net_usage = 0ULL;
#       uint64_t pending_cpu_usage = 0ULL;

#       uint64_t total_net_weight = 0ULL;
#       uint64_t total_cpu_weight = 0ULL;
#       uint64_t total_ram_bytes = 0ULL;

#       /**
#        * The virtual number of bytes that would be consumed over blocksize_average_window_ms
#        * if all blocks were at their maximum virtual size. This is virtual because the
#        * real maximum block is less, this virtual number is only used for rate limiting users.
#        *
#        * It's lowest possible value is max_block_size * blocksize_average_window_ms / block_interval
#        * It's highest possible value is config::maximum_elastic_resource_multiplier (1000) times its lowest possible value
#        *
#        * This means that the most an account can consume during idle periods is 1000x the bandwidth
#        * it is gauranteed under congestion.
#        *
#        * Increases when average_block_size < target_block_size, decreases when
#        * average_block_size > target_block_size, with a cap at 1000x max_block_size
#        * and a floor at max_block_size;
#        **/
#       uint64_t virtual_net_limit = 0ULL;

#       /**
#        *  Increases when average_bloc
#        */
#       uint64_t virtual_cpu_limit = 0ULL;

#    };

#    using resource_limits_state_index = chainbase::shared_multi_index_container<
#       resource_limits_state_object,
#       indexed_by<
#          ordered_unique<tag<by_id>, member<resource_limits_state_object, resource_limits_state_object::id_type, &resource_limits_state_object::id>>
#       >
#    >;

@chain_test(True)
def test_resource_limits_state_object(tester: ChainTester):
    deploy_contract(tester, 'test')
    def parse_resource_limits_state(data):
#       usage_accumulator average_block_net_usage;
#       usage_accumulator average_block_cpu_usage;
#       uint64_t pending_net_usage = 0ULL;
#       uint64_t pending_cpu_usage = 0ULL;
#       uint64_t total_net_weight = 0ULL;
#       uint64_t total_cpu_weight = 0ULL;
#       uint64_t total_ram_bytes = 0ULL;
#       uint64_t virtual_net_limit = 0ULL;
#       uint64_t virtual_cpu_limit = 0ULL;
        dec = Decoder(data)
        average_block_net_usage = UsageAccumulator.unpack(dec)
        average_block_cpu_usage = UsageAccumulator.unpack(dec)
        pending_net_usage = dec.unpack_u64()
        pending_cpu_usage = dec.unpack_u64()
        total_net_weight = dec.unpack_u64()
        total_cpu_weight = dec.unpack_u64()
        total_ram_bytes = dec.unpack_u64()
        virtual_net_limit = dec.unpack_u64()
        virtual_cpu_limit = dec.unpack_u64()
        return (average_block_net_usage,
            average_block_cpu_usage,
            pending_net_usage,
            pending_cpu_usage,
            total_net_weight,
            total_cpu_weight,
            total_ram_bytes,
            virtual_net_limit,
            virtual_cpu_limit,
        )

    def on_data(tp, data):
        parse_resource_limits_state(data)

    data = tester.db.find(database.resource_limits_state_object_type, 0, 0)
    print(parse_resource_limits_state(data))

class ElasticLimitParameters(object):
    def __init__(self, target, max_, periods):
        self.target = target
        self.max_ = max_
        self.periods = periods

    def __repr__(self):
        return f"(target: {self.target}, max_: {self.max_}, periods: {self.periods})"

    @classmethod
    def unpack(cls, dec):
        target = dec.unpack_u64()
        max_ = dec.unpack_u64()
        periods = dec.unpack_u32()
        return ElasticLimitParameters(target, max_, periods)

class Ratio(object):
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator

    def __repr__(self):
        return f"(numerator: {self.numerator}, denominator: {self.denominator})"

    @classmethod
    def unpack(cls, dec):
        numerator = dec.unpack_u64()
        denominator = dec.unpack_u64()
        return Ratio(numerator, denominator)

class ResourceLimitsConfig(object):
    def __init__(self, cpu_limit_parameters, net_limit_parameters, max_multiplier, contract_rate, expand_rate):
        self.cpu_limit_parameters = cpu_limit_parameters
        self.net_limit_parameters = net_limit_parameters
        self.max_multiplier = max_multiplier
        self.contract_rate = contract_rate
        self.expand_rate = expand_rate

    def __repr__(self):
        return f"""
cpu_limit_parameters: {self.cpu_limit_parameters},
net_limit_parameters: {self.net_limit_parameters},
max_multiplier: {self.max_multiplier},
contract_rate: {self.contract_rate},
expand_rate: {self.expand_rate}
"""

    @classmethod
    def unpack(cls, dec: Decoder):
        cpu_limit_parameters = ElasticLimitParameters.unpack(dec)
        net_limit_parameters = ElasticLimitParameters.unpack(dec)
        max_multiplier = dec.unpack_u32()
        contract_rate = Ratio.unpack(dec)
        expand_rate = Ratio.unpack(dec)
        return ResourceLimitsConfig(
            cpu_limit_parameters,
            net_limit_parameters,
            max_multiplier,
            contract_rate,
            expand_rate,
        )

@chain_test(True)
def test_resource_limits_config(tester: ChainTester):
# class resource_limits_config_object : public chainbase::object<resource_limits_config_object_type, resource_limits_config_object> {
#     OBJECT_CTOR(resource_limits_config_object);
#     id_type id;

#     elastic_limit_parameters cpu_limit_parameters = {EOS_PERCENT(config::default_max_block_cpu_usage, config::default_target_block_cpu_usage_pct), config::default_max_block_cpu_usage, config::block_cpu_usage_average_window_ms / config::block_interval_ms, 1000, {99, 100}, {1000, 999}};
#     elastic_limit_parameters net_limit_parameters = {EOS_PERCENT(config::default_max_block_net_usage, config::default_target_block_net_usage_pct), config::default_max_block_net_usage, config::block_size_average_window_ms / config::block_interval_ms, 1000, {99, 100}, {1000, 999}};

    #    struct elastic_limit_parameters {
    #       uint64_t target;           // the desired usage
    #       uint64_t max;              // the maximum usage
    #       uint32_t periods;          // the number of aggregation periods that contribute to the average usage

#       uint32_t max_multiplier;   // the multiplier by which virtual space can oversell usage when uncongested
#       ratio    contract_rate;    // the rate at which a congested resource contracts its limit
#       ratio    expand_rate;       // the rate at which an uncongested resource expands its limits

#    namespace impl {
#       template<typename T>
#       struct ratio {
#          T numerator;
#          T denominator;

#    using ratio = impl::ratio<uint64_t>;


#       friend inline bool operator !=( const elastic_limit_parameters& lhs, const elastic_limit_parameters& rhs ) {
#          return !(lhs == rhs);
#       }

#     uint32_t account_cpu_usage_average_window = config::account_cpu_usage_average_window_ms / config::block_interval_ms;
#     uint32_t account_net_usage_average_window = config::account_net_usage_average_window_ms / config::block_interval_ms;

    def parse_resource_limits_config(data):
        dec = Decoder(data)
        return ResourceLimitsConfig.unpack(dec)

    data = tester.db.find(database.resource_limits_config_object_type, 0, 0)
    print(parse_resource_limits_config(data))



#    class protocol_state_object : public chainbase::object<protocol_state_object_type, protocol_state_object>
#    {
#       OBJECT_CTOR(protocol_state_object, (activated_protocol_features)(preactivated_protocol_features)(whitelisted_intrinsics))

#    public:
#       struct activated_protocol_feature {
#          digest_type feature_digest;
#          uint32_t    activation_block_num = 0;

#          activated_protocol_feature() = default;

#          activated_protocol_feature( const digest_type& feature_digest, uint32_t activation_block_num )
#          :feature_digest( feature_digest )
#          ,activation_block_num( activation_block_num )
#          {}

#          bool operator==(const activated_protocol_feature& rhs) const {
#             return feature_digest == rhs.feature_digest && activation_block_num == rhs.activation_block_num;
#          }
#       };

#    public:
#       id_type                                    id;
#       shared_vector<activated_protocol_feature>  activated_protocol_features;
#       shared_vector<digest_type>                 preactivated_protocol_features;
#       whitelisted_intrinsics_type                whitelisted_intrinsics;
#       uint32_t                                   num_supported_key_types = 0;
#    };

class ActivatedProtocolFeature(object):
    def __init__(self, feature_digest, activation_block_num):
        self.feature_digest = feature_digest
        self.activation_block_num = activation_block_num

    def __repr__(self):
        return f'(feature_digest: "{self.feature_digest}", activation_block_num: {self.activation_block_num})'

    @classmethod
    def unpack(cls, dec):
        feature_digest = dec.unpack_checksum256()
        activation_block_num = dec.unpack_u32()
        return ActivatedProtocolFeature(feature_digest, activation_block_num)

class WhitelistedIntrinsics(object):
    def __init__(self, intrinsics):
        self.intrinsics = intrinsics

    def __repr__(self):
        return str(self.intrinsics)

    @classmethod
    def unpack(cls, dec):
        length = dec.unpack_length()
        d = {}
        for i in range(length):
            a = dec.unpack_u64()
            b = dec.unpack_string()
            d[a] = b
        return WhitelistedIntrinsics(d)

@chain_test(True)
def test_protocol_state_object(tester: ChainTester):
    def parse_protocol_state_object(data):
        dec = Decoder(data)
        table_id = dec.unpack_u64()
        activated_protocol_feature_size = dec.unpack_length()

        features = []
        for i in range(activated_protocol_feature_size):
            features.append(ActivatedProtocolFeature.unpack(dec))

        preactivated_protocol_features = []
        preactivated_protocol_features_size = dec.unpack_length()

        for i in range(preactivated_protocol_features_size):
            preactivated_protocol_features.append(dec.unpack_checksum256())
        
        whitelisted_intrinsics = WhitelistedIntrinsics.unpack(dec)
        num_supported_key_types = dec.unpack_u32()
        print(table_id)
        for feature in features:
            print(feature)

        print(preactivated_protocol_features)
        print(whitelisted_intrinsics.intrinsics)
        print(num_supported_key_types)

    data = tester.db.find(database.protocol_state_object_type, 0, 0)
    parse_protocol_state_object(data)


#    class account_ram_correction_object : public chainbase::object<account_ram_correction_object_type, account_ram_correction_object>
#       id_type      id;
#       account_name name; //< name should not be changed within a chainbase modifier lambda
#       uint64_t     ram_correction = 0;
#    };

#    struct by_name;
#    using account_ram_correction_index = chainbase::shared_multi_index_container<
#       account_ram_correction_object,
#          ordered_unique<tag<by_id>, member<account_ram_correction_object, account_ram_correction_object::id_type, &account_ram_correction_object::id>>,
#          ordered_unique<tag<by_name>, member<account_ram_correction_object, account_name, &account_ram_correction_object::name>>

@chain_test(True)
def test_account_ram_correction_object(tester: ChainTester):

    def parse_account_ram_correction_object(data):
        dec = Decoder(data)
        table_id = dec.unpack_i64()
        name = dec.unpack_name()
        ram_correction = dec.unpack_u64()
        print(table_id, name, ram_correction)

    data = tester.db.find(database.account_ram_correction_object_type, 0, 0)
    print(data)
    if data:
        parse_account_ram_correction_object(data)


# class code_object : public chainbase::object<code_object_type, code_object> {
#     id_type      id;
#     digest_type  code_hash; //< code_hash should not be changed within a chainbase modifier lambda
#     shared_blob  code;
#     uint64_t     code_ref_count;
#     uint32_t     first_block_used;
#     uint8_t      vm_type = 0; //< vm_type should not be changed within a chainbase modifier lambda
#     uint8_t      vm_version = 0; //< vm_version should not be changed within a chainbase modifier lambda
# };

# struct by_code_hash;
# using code_index = chainbase::shared_multi_index_container<
#         ordered_unique<tag<by_id>, member<code_object, code_object::id_type, &code_object::id>>,
#         ordered_unique<tag<by_code_hash>,
#             member<code_object, digest_type, &code_object::code_hash>,
#             member<code_object, uint8_t,     &code_object::vm_type>,
#             member<code_object, uint8_t,     &code_object::vm_version>


@chain_test(True)
def test_code_object(tester: ChainTester):

    def parse_code_object(data):
        dec = Decoder(data)
        table_id = dec.unpack_i64()
        code_hash = dec.unpack_checksum256()
        code = dec.unpack_bytes()
        code_ref_count = dec.unpack_u64()
        first_block_used = dec.unpack_u32()
        vm_type = dec.unpack_u8()
        vm_version = dec.unpack_u8()
        print(code_hash, code_ref_count, first_block_used)

    def on_data(tp, data):
        parse_code_object(data)
        return 1

    data = tester.db.find(database.code_object_type, 0, 0)
    # print(data)
    if data:
        parse_code_object(data)

#         ordered_unique<tag<by_code_hash>,
#             member<code_object, digest_type, &code_object::code_hash>,
#             member<code_object, uint8_t,     &code_object::vm_type>,
#             member<code_object, uint8_t,     &code_object::vm_version>
    print('+++++++++by table id')
    tester.db.walk(database.code_object_type, 0, on_data)
    print('+++++++by_code_hash')
    tester.db.walk(database.code_object_type, 1, on_data)

    print('+++++++++walk range by id')
    lower_bound = 0
    upper_bound = b'\xff'*7 + b'\x7f'
    tester.db.walk_range(database.code_object_type, 0, lower_bound, upper_bound, on_data)

    print('+++++++=walk range by code hash')
    lower_bound = b'\x00'*(32+1+1)
    upper_bound = b'\xff'*(32+1+1)
    tester.db.walk_range(database.code_object_type, 1, lower_bound, upper_bound, on_data)

    data = tester.db.lower_bound(database.code_object_type, 0, 0)
    assert data
    data = tester.db.upper_bound(database.code_object_type, 0, 0)
    assert data

    key = b'\x00'*(32+1+1)
    data = tester.db.lower_bound(database.code_object_type, 1, key)
    assert data
    data = tester.db.upper_bound(database.code_object_type, 1, key)
    assert data

# class database_header_object : public chainbase::object<database_header_object_type, database_header_object>
# {
#     OBJECT_CTOR(database_header_object)

#     /**
#     *  VERSION HISTORY
#     *   - 0 : implied version when this header is absent
#     *   - 1 : initial version, prior to this no `database_header_object` existed in the shared memory file but
#     *         no changes to its format were made so it can be safely added to existing databases
#     *   - 2 : shared_authority now holds shared_key_weights & shared_public_keys
#     *         change from producer_key to producer_authority for many in-memory structures
#     */

#     static constexpr uint32_t current_version            = 2;
#     static constexpr uint32_t minimum_version            = 2;

#     id_type        id;
#     uint32_t       version = current_version;

#     void validate() const {
#     EOS_ASSERT(std::clamp(version, minimum_version, current_version) == version, bad_database_version_exception,
#                 "state database version is incompatible, please restore from a compatible snapshot or replay!",
#                 ("version", version)("minimum_version", minimum_version)("maximum_version", current_version));
#     }
# };

# struct by_block_id;
# using database_header_multi_index = chainbase::shared_multi_index_container<
#     database_header_object,
#     indexed_by<
#             ordered_unique<tag<by_id>, BOOST_MULTI_INDEX_MEMBER(database_header_object, database_header_object::id_type, id)>
#         >
# >;

@chain_test(True)
def test_database_header_object(tester: ChainTester):

    def parse_database_header_object(data):
        dec = Decoder(data)
        table_id = dec.unpack_i64()
        version = dec.unpack_u32()
        print(table_id, version)

    data = tester.db.find(database.database_header_object_type, 0, 0)
    print(data)
    if data:
        parse_database_header_object(data)