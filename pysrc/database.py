from typing import Tuple, Union

from . import log
from .native_modules import _database, _eos
from .database_objects import *
from .packer import Decoder, Encoder
from .types import F64, I64, U8, U16, U32, U64, Checksum256, Name
from .utils import f2b, i2b, to_bytes, u2b
from .chain_exceptions import get_last_exception

null_object_type = 0
account_object_type = 1
account_metadata_object_type = 2
permission_object_type = 3
permission_usage_object_type = 4
permission_link_object_type = 5
# UNUSED_action_code_object_type,

key_value_object_type = 7
index64_object_type = 8
index128_object_type = 9
index256_object_type = 10
index_double_object_type = 11
index_long_double_object_type = 12

global_property_object_type = 13
dynamic_global_property_object_type = 14
block_summary_object_type = 15
transaction_object_type = 16
generated_transaction_object_type = 17
# UNUSED_producer_object_type = 18
# UNUSED_chain_property_object_type = 19
# account_control_history_object_type = 20 #     ///< Defined by history_plugin
# UNUSED_account_transaction_history_object_type = 21
# UNUSED_transaction_history_object_type = 22
# public_key_history_object_type = 23          ///< Defined by history_plugin
# UNUSED_balance_object_type = 24
# UNUSED_staked_balance_object_type = 25
# UNUSED_producer_votes_object_type = 26
# UNUSED_producer_schedule_object_type = 27
# UNUSED_proxy_vote_object_type = 28
# UNUSED_scope_sequence_object_type = 29
table_id_object_type = 30
resource_limits_object_type = 31
resource_usage_object_type = 32
resource_limits_state_object_type = 33
resource_limits_config_object_type = 34
# UNUSED_account_history_object_type = 35 #              ///< Defined by history_plugin
# UNUSED_action_history_object_type = 36 #               ///< Defined by history_plugin
# UNUSED_reversible_block_object_type = 37
protocol_state_object_type = 38
account_ram_correction_object_type = 39
code_object_type = 40
database_header_object_type = 41

def parse_return_value(ret: int):
    if ret == -2:
        raise Exception(_eos.get_last_error())
    assert ret in (0, 1)
    if ret:
        return True
    return False

logger = log.get_logger(__name__)

class Database:
    def __init__(self, db_ptr: int = 0, attach: bool=True):
        if not db_ptr:
            # default to get db ptr from chain_plugin.chain.db()
            db_ptr = _eos.get_database()
        self.ptr = _database.new_proxy(db_ptr, attach)
        self.attach = attach
        logger.info("+++++total memory: %.2fMB, used memory: %.2fMB, free memory: %.2fMB", self.total_memory()/1024/1024, self.used_memory()/1024/1024, self.free_memory()/1024/1024)

    def total_memory(self):
        return _database.get_total_memory(self.ptr)

    def free_memory(self):
        return _database.get_free_memory(self.ptr)

    def used_memory(self):
        return self.total_memory() - self.free_memory()

    def create(self, tp, raw_data: bytes):
        ret = _database.create(self.ptr, tp, raw_data)
        if ret == -2:
            raise Exception(_eos.get_last_error())
        assert ret in (0, 1)
        if ret:
            return True
        return False

    def modify(self, tp: int, index_position: int, raw_key: bytes, raw_data: bytes):
        ret = _database.modify(self.ptr, tp, index_position, raw_key, raw_data)
        if ret == -2:
            raise Exception(_eos.get_last_error())
        assert ret in (0, 1)
        if ret:
            return True
        return False

    def walk(self, tp: int, index_position: int, cb, custom_data = None):
        ret = _database.walk(self.ptr, tp, index_position, cb, custom_data)
        if ret == -2:
            raise Exception(_eos.get_last_error())
        return ret

    def walk_range(self, tp: int, index_position: int, lower_bound: Union[int, bytes], upper_bound: Union[int, bytes], cb, custom_data = None):
        if index_position == 0:
            if isinstance(lower_bound, int):
                lower_bound = i2b(lower_bound)
            if isinstance(upper_bound, int):
                upper_bound = i2b(upper_bound)

        ret = _database.walk_range(self.ptr, tp, index_position, lower_bound, upper_bound, cb, custom_data)
        if ret == -2:
            raise Exception(_eos.get_last_error())
        return ret

    def find(self, tp: int, index_position: int, key: Union[int, bytes]):
        if index_position == 0 and isinstance(key, int):
            key = i2b(key)
        ret, data = _database.find(self.ptr, tp, index_position, key)
        if ret == -2:
            raise Exception(_eos.get_last_error())
        if ret == 0:
            return None
        return data

    def lower_bound(self, tp: int, index_position: int, key: Union[int, bytes]):
        if index_position == 0 and isinstance(key, int):
            key = i2b(key)
        ret, data = _database.lower_bound(self.ptr, tp, index_position, key)
        if ret == -2:
            raise Exception(_eos.get_last_error())
        if ret == 0:
            return None
        return data

    def upper_bound(self, tp: int, index_position: int, key: Union[int, bytes]):
        if index_position == 0 and isinstance(key, int):
            key = i2b(key, 8)

        ret, data = _database.upper_bound(self.ptr, tp, index_position, key)
        if ret == -2:
            raise Exception(_eos.get_last_error())
        if ret == 0:
            return None
        return data

    def row_count(self, tp: int):
        ret = _database.row_count(self.ptr, tp)
        if ret == -2:
            raise Exception(f"invalid database object type: {tp}")
        return ret

# account_object_type = 1
class AccountObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: AccountObject):
        enc = Encoder()
        enc.pack(obj)
        ret = self.db.create(account_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(account_object_type, AccountObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return AccountObject.unpack(dec)

    def find_by_name(self, account: Name):
        key = eos.s2b(account)
        data = self.db.find(account_object_type, AccountObject.by_name, key)
        if not data:
            return None
        dec = Decoder(data)
        return AccountObject.unpack(dec)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = AccountObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(account_object_type, AccountObject.by_id, self.on_object_data, (cb, raw_data, user_data))
    
    def walk_by_name(self, cb, user_data=None, raw_data=False):
        return self.db.walk(account_object_type, AccountObject.by_name, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(account_object_type, AccountObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_name(self, lower_bound: Name, upper_bound: Name, cb, user_data=None, raw_data=False):
        lower_bound = eos.s2b(lower_bound)
        upper_bound = eos.s2b(upper_bound)
        return self.db.walk_range(account_object_type, AccountObject.by_name, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(account_object_type, AccountObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return AccountObject.unpack(dec)

    def lower_bound_by_name(self, lower_bound: Name):
        lower_bound = eos.s2b(lower_bound)
        data = self.db.lower_bound(account_object_type, AccountObject.by_name, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return AccountObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(account_object_type, AccountObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return AccountObject.unpack(dec)

    def upper_bound_by_name(self, upper_bound: Name):
        upper_bound = eos.s2b(upper_bound)
        data = self.db.upper_bound(account_object_type, AccountObject.by_name, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return AccountObject.unpack(dec)

    def modify(self, perm: AccountObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(account_object_type, AccountObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(account_object_type)

# account_metadata_object_type = 2
class AccountMetadataObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: AccountMetadataObject):
        enc = Encoder()
        enc.pack(obj)
        ret = self.db.create(account_metadata_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(account_metadata_object_type, AccountMetadataObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return AccountMetadataObject.unpack(dec)
    
    def find_by_name(self, name: Name):
        key = eos.s2b(name)
        data = self.db.find(account_metadata_object_type, AccountMetadataObject.by_name, key)
        if not data:
            return None
        dec = Decoder(data)
        return AccountMetadataObject.unpack(dec)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = AccountMetadataObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(account_metadata_object_type, AccountMetadataObject.by_id, self.on_object_data, (cb, raw_data, user_data))
    
    def walk_by_name(self, cb, user_data=None, raw_data=False):
        return self.db.walk(account_metadata_object_type, AccountMetadataObject.by_name, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(account_metadata_object_type, AccountMetadataObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_name(self, lower_bound: Name, upper_bound: Name, cb, user_data=None, raw_data=False):
        lower_bound = eos.s2b(lower_bound)
        upper_bound = eos.s2b(upper_bound)
        return self.db.walk_range(account_metadata_object_type, AccountMetadataObject.by_name, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(account_metadata_object_type, AccountMetadataObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return AccountMetadataObject.unpack(dec)

    def lower_bound_by_name(self, lower_bound: Name):
        lower_bound = eos.s2b(lower_bound)
        data = self.db.lower_bound(account_metadata_object_type, AccountMetadataObject.by_name, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return AccountMetadataObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(account_metadata_object_type, AccountMetadataObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return AccountMetadataObject.unpack(dec)

    def upper_bound_by_name(self, upper_bound: Name):
        upper_bound = eos.s2b(upper_bound)
        data = self.db.upper_bound(account_metadata_object_type, AccountMetadataObject.by_name, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return AccountMetadataObject.unpack(dec)

    def modify(self, perm: AccountMetadataObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(account_metadata_object_type, AccountMetadataObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(account_metadata_object_type)

# permission_object_type = 3
class PermissionObjectIndex(object):
    
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: PermissionObject):
        enc = Encoder()
        enc.pack(obj)
        ret = self.db.create(permission_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(permission_object_type, PermissionObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)
    
    def find_by_parent(self, parent: I64, table_id: I64):
        """
        permission_object::parent permission_object::id
        """
        key = PermissionObject.generate_key_by_parent(parent, table_id)
        data = self.db.find(permission_object_type, PermissionObject.by_parent, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)

    def find_by_owner(self, owner: Name, name: Name):
        key = PermissionObject.generate_key_by_owner(owner, name)
        data = self.db.find(permission_object_type, PermissionObject.by_owner, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)

    def find_by_name(self, name: Name, table_id: I64):
        """
        permission_object::name permission_object::id
        """
        key = PermissionObject.generate_key_by_name(name, table_id)
        data = self.db.find(permission_object_type, PermissionObject.by_name, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)

    def modify(self, perm: PermissionObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(permission_object_type, PermissionObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(permission_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = PermissionObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(permission_object_type, PermissionObject.by_id, self.on_object_data, (cb, raw_data, user_data))
    
    def walk_by_parent(self, cb, user_data=None, raw_data=False):
        return self.db.walk(permission_object_type, PermissionObject.by_parent, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_owner(self, cb, user_data=None, raw_data=False):
        return self.db.walk(permission_object_type, PermissionObject.by_owner, self.on_object_data, (cb, raw_data, user_data))
    
    def walk_by_name(self, cb, user_data=None, raw_data=False):
        return self.db.walk(permission_object_type, PermissionObject.by_name, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(permission_object_type, PermissionObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_parent(self, lower_bound: Tuple[I64, I64], upper_bound: Tuple[I64, I64], cb, user_data=None, raw_data=False):
        lower_bound = PermissionObject.generate_key_by_parent(*lower_bound)
        upper_bound = PermissionObject.generate_key_by_parent(*upper_bound)
        return self.db.walk_range(permission_object_type, PermissionObject.by_parent, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_owner(self, lower_bound: Tuple[Name, Name], upper_bound: Tuple[Name, Name], cb, user_data=None, raw_data=False):
        lower_bound = PermissionObject.generate_key_by_owner(*lower_bound)
        upper_bound = PermissionObject.generate_key_by_owner(*upper_bound)
        return self.db.walk_range(permission_object_type, PermissionObject.by_owner, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_name(self, lower_bound: Tuple[Name, I64], upper_bound: Tuple[Name, I64], cb, user_data=None, raw_data=False):
        lower_bound = PermissionObject.generate_key_by_name(*lower_bound)
        upper_bound = PermissionObject.generate_key_by_name(*upper_bound)
        return self.db.walk_range(permission_object_type, PermissionObject.by_name, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.lower_bound(permission_object_type, PermissionObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)

    def lower_bound_by_parent(self, parent: I64, table_id: I64):
        key = PermissionObject.generate_key_by_parent(parent, table_id)
        data = self.db.lower_bound(permission_object_type, PermissionObject.by_parent, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)
    
    def lower_bound_by_owner(self, owner: Name, name: Name):
        key = PermissionObject.generate_key_by_owner(owner, name)
        data = self.db.lower_bound(permission_object_type, PermissionObject.by_owner, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)

    def lower_bound_by_name(self, name: Name, table_id: I64):
        key = PermissionObject.generate_key_by_name(name, table_id)
        data = self.db.lower_bound(permission_object_type, PermissionObject.by_name, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)

    def upper_bound_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.upper_bound(permission_object_type, PermissionObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)

    def upper_bound_by_parent(self, parent: I64, table_id: I64):
        key = PermissionObject.generate_key_by_parent(parent, table_id)
        data = self.db.upper_bound(permission_object_type, PermissionObject.by_parent, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)

    def upper_bound_by_owner(self, owner: Name, name: Name):
        key = PermissionObject.generate_key_by_owner(owner, name)
        data = self.db.upper_bound(permission_object_type, PermissionObject.by_owner, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)
    
    def upper_bound_by_name(self, name: Name, table_id: I64):
        key = PermissionObject.generate_key_by_name(name, table_id)
        data = self.db.upper_bound(permission_object_type, PermissionObject.by_name, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionObject.unpack(dec)

# permission_usage_object_type = 4
class PermissionUsageObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, perm: PermissionUsageObject):
        enc = Encoder()
        enc.pack(perm)
        ret = self.db.create(permission_usage_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(permission_usage_object_type, PermissionUsageObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionUsageObject.unpack(dec)

    def modify(self, perm: PermissionUsageObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(permission_usage_object_type, PermissionUsageObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(permission_usage_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = PermissionUsageObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(permission_usage_object_type, PermissionUsageObject.by_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(permission_usage_object_type, PermissionUsageObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(permission_usage_object_type, PermissionUsageObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionUsageObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(permission_usage_object_type, PermissionUsageObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionUsageObject.unpack(dec)

# permission_link_object_type = 5
class PermissionLinkObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, perm: PermissionLinkObject):
        enc = Encoder()
        enc.pack(perm)
        ret = self.db.create(permission_link_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(permission_link_object_type, PermissionLinkObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionLinkObject.unpack(dec)
    
    def find_by_action_name(self, action: Name, code: Name, message_type: Name):
        key = PermissionLinkObject.generate_key_by_action_name(action, code, message_type)
        data = self.db.find(permission_link_object_type, PermissionLinkObject.by_action_name, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionLinkObject.unpack(dec)

    def find_by_permission_name(self, account: Name, required_permission: Name, table_id: I64):
        key = PermissionLinkObject.generate_key_by_permission_name(account, required_permission, table_id)
        data = self.db.find(permission_link_object_type, PermissionLinkObject.by_permission_name, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionLinkObject.unpack(dec)

    def modify(self, perm: PermissionLinkObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(permission_link_object_type, PermissionLinkObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(permission_link_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = PermissionLinkObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(permission_link_object_type, PermissionLinkObject.by_id, self.on_object_data, (cb, raw_data, user_data))
    
    def walk_by_action_name(self, cb, user_data=None, raw_data=False):
        return self.db.walk(permission_link_object_type, PermissionLinkObject.by_action_name, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_permission_name(self, cb, user_data=None, raw_data=False):
        return self.db.walk(permission_link_object_type, PermissionLinkObject.by_permission_name, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(permission_link_object_type, PermissionLinkObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_action_name(self, lower_bound: Tuple[Name, Name, Name], upper_bound: Tuple[Name, Name, Name], cb, user_data=None, raw_data=False):
        lower_bound = PermissionLinkObject.generate_key_by_action_name(*lower_bound)
        upper_bound = PermissionLinkObject.generate_key_by_action_name(*upper_bound)
        return self.db.walk_range(permission_link_object_type, PermissionLinkObject.by_action_name, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_permission_name(self, lower_bound: Tuple[Name, Name, I64], upper_bound: Tuple[Name, Name, I64], cb, user_data=None, raw_data=False):
        lower_bound = PermissionLinkObject.generate_key_by_permission_name(*lower_bound)
        upper_bound = PermissionLinkObject.generate_key_by_permission_name(*upper_bound)
        return self.db.walk_range(permission_link_object_type, PermissionLinkObject.by_permission_name, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(permission_link_object_type, PermissionLinkObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionLinkObject.unpack(dec)

    def lower_bound_by_action_name(self, lower_bound: Tuple[Name, Name, Name]):
        lower_bound = PermissionLinkObject.generate_key_by_action_name(*lower_bound)
        data = self.db.lower_bound(permission_link_object_type, PermissionLinkObject.by_action_name, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionLinkObject.unpack(dec)

    def lower_bound_by_permission_name(self, lower_bound: Tuple[Name, Name, I64]):
        lower_bound = PermissionLinkObject.generate_key_by_permission_name(*lower_bound)
        data = self.db.lower_bound(permission_link_object_type, PermissionLinkObject.by_permission_name, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionLinkObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(permission_link_object_type, PermissionLinkObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionLinkObject.unpack(dec)

    def upper_bound_by_action_name(self, upper_bound: Tuple[Name, Name, Name]):
        upper_bound = PermissionLinkObject.generate_key_by_action_name(*upper_bound)
        data = self.db.upper_bound(permission_link_object_type, PermissionLinkObject.by_action_name, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionLinkObject.unpack(dec)

    def upper_bound_by_permission_name(self, upper_bound: Tuple[Name, Name, I64]):
        upper_bound = PermissionLinkObject.generate_key_by_permission_name(*upper_bound)
        data = self.db.upper_bound(permission_link_object_type, PermissionLinkObject.by_permission_name, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionLinkObject.unpack(dec)


# key_value_object_type = 7
class KeyValueObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, perm: KeyValueObject):
        enc = Encoder()
        perm.pack(enc)
        ret = self.db.create(key_value_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(key_value_object_type, KeyValueObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return KeyValueObject.unpack(dec)
    
    def find_by_scope_primary(self, t_id: I64, primary_key: U64):
        key = KeyValueObject.generate_key_by_scope_primary(t_id, primary_key)
        data = self.db.find(key_value_object_type, KeyValueObject.by_scope_primary, key)
        if not data:
            return None
        dec = Decoder(data)
        return KeyValueObject.unpack(dec)

    def modify(self, perm: KeyValueObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(key_value_object_type, KeyValueObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(key_value_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = KeyValueObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(key_value_object_type, KeyValueObject.by_id, self.on_object_data, (cb, raw_data, user_data))
    
    def walk_by_scope_primary(self, cb, user_data=None, raw_data=False):
        return self.db.walk(key_value_object_type, KeyValueObject.by_scope_primary, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(key_value_object_type, KeyValueObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_scope_primary(self, lower_bound: Tuple[I64, U64], upper_bound: Tuple[I64, U64], cb, user_data=None, raw_data=False):
        lower_bound = KeyValueObject.generate_key_by_scope_primary(*lower_bound)
        upper_bound = KeyValueObject.generate_key_by_scope_primary(*upper_bound)
        return self.db.walk_range(key_value_object_type, KeyValueObject.by_scope_primary, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(key_value_object_type, KeyValueObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return KeyValueObject.unpack(dec)

    def lower_bound_by_scope_primary(self, lower_bound: Tuple[I64, U64]):
        lower_bound = KeyValueObject.generate_key_by_scope_primary(*lower_bound)
        data = self.db.lower_bound(key_value_object_type, KeyValueObject.by_scope_primary, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return KeyValueObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(key_value_object_type, KeyValueObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return KeyValueObject.unpack(dec)
    
    def upper_bound_by_scope_primary(self, upper_bound: Tuple[I64, U64]):
        upper_bound = KeyValueObject.generate_key_by_scope_primary(*upper_bound)
        data = self.db.upper_bound(key_value_object_type, KeyValueObject.by_scope_primary, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return KeyValueObject.unpack(dec)

# index64_object_type = 8
class Index64ObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: Index64Object):
        enc = Encoder()
        enc.pack(obj)
        ret = self.db.create(index64_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(index64_object_type, Index64Object.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index64Object.unpack(dec)
    
    def find_by_primary(self, t_id: I64, primary_key: U64):
        key = i2b(t_id) + u2b(primary_key)
        data = self.db.find(index64_object_type, Index64Object.by_primary, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index64Object.unpack(dec)

    def find_by_secondary(self, t_id: I64, secondary_key: U64, primary_key: U64):
        key = i2b(t_id) + u2b(secondary_key) + u2b(primary_key)
        data = self.db.find(index64_object_type, Index64Object.by_secondary, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index64Object.unpack(dec)

    def modify(self, perm: Index64Object):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(index64_object_type, Index64Object.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(index64_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = Index64Object.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index64_object_type, Index64Object.by_id, self.on_object_data, (cb, raw_data, user_data))
    
    def walk_by_primary(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index64_object_type, Index64Object.by_primary, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_secondary(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index64_object_type, Index64Object.by_secondary, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = u2b(lower_bound)
        upper_bound = u2b(upper_bound)
        return self.db.walk_range(index64_object_type, Index64Object.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_primary(self, lower_bound: Tuple[I64, U64], upper_bound: Tuple[I64, U64], cb, user_data=None, raw_data=False):
        lower_bound = Index64Object.generate_key_by_primary(*lower_bound)
        upper_bound = Index64Object.generate_key_by_primary(*upper_bound)
        return self.db.walk_range(index64_object_type, Index64Object.by_primary, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_secondary(self, lower_bound: Tuple[I64, U64, U64], upper_bound: Tuple[I64, U64, U64], cb, user_data=None, raw_data=False):
        lower_bound = Index64Object.generate_key_by_secondary(*lower_bound)
        upper_bound = Index64Object.generate_key_by_secondary(*upper_bound)
        return self.db.walk_range(index64_object_type, Index64Object.by_secondary, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = u2b(lower_bound)
        data = self.db.lower_bound(index64_object_type, Index64Object.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index64Object.unpack(dec)

    def lower_bound_by_primary(self, t_id: I64, primary_key: U64):
        lower_bound = Index64Object.generate_key_by_primary(t_id, primary_key)
        data = self.db.lower_bound(index64_object_type, Index64Object.by_primary, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index64Object.unpack(dec)

    def lower_bound_by_secondary(self, t_id: I64, secondary_key: U64, primary_key: U64):
        lower_bound = Index64Object.generate_key_by_secondary(t_id, secondary_key, primary_key)
        data = self.db.lower_bound(index64_object_type, Index64Object.by_secondary, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index64Object.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = u2b(upper_bound)
        data = self.db.upper_bound(index64_object_type, Index64Object.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index64Object.unpack(dec)

    def upper_bound_by_primary(self, t_id: I64, primary_key: U64):
        upper_bound = Index64Object.generate_key_by_primary(t_id, primary_key)
        data = self.db.upper_bound(index64_object_type, Index64Object.by_primary, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index64Object.unpack(dec)
    
    def upper_bound_by_secondary(self, t_id: I64, secondary_key: U64, primary_key: U64):
        upper_bound = Index64Object.generate_key_by_secondary(t_id, secondary_key, primary_key)
        data = self.db.upper_bound(index64_object_type, Index64Object.by_secondary, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index64Object.unpack(dec)

# index128_object_type = 9
class Index128ObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: Index128Object):
        enc = Encoder()
        obj.pack(enc)
        ret = self.db.create(index128_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(index128_object_type, Index128Object.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index128Object.unpack(dec)
    
    def find_by_primary(self, t_id: I64, primary_key: U64):
        key = i2b(t_id) + u2b(primary_key)
        data = self.db.find(index128_object_type, Index128Object.by_primary, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index128Object.unpack(dec)
    
    def find_by_secondary(self, t_id: I64, secondary_key: U128, primary_key: U64):
        key = i2b(t_id) + u2b(secondary_key, 16) + u2b(primary_key)
        data = self.db.find(index128_object_type, Index128Object.by_secondary, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index128Object.unpack(dec)

    def modify(self, perm: Index128Object):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(index128_object_type, Index128Object.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(index128_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = Index128Object.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index128_object_type, Index128Object.by_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_primary(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index128_object_type, Index128Object.by_primary, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_secondary(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index128_object_type, Index128Object.by_secondary, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(index128_object_type, Index128Object.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_primary(self, lower_bound: Tuple[I64, U64], upper_bound: Tuple[I64, U64], cb, user_data=None, raw_data=False):
        lower_bound = Index128Object.generate_key_by_primary(*lower_bound)
        upper_bound = Index128Object.generate_key_by_primary(*upper_bound)
        return self.db.walk_range(index128_object_type, Index128Object.by_primary, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_secondary(self, lower_bound: Tuple[I64, U128, U64], upper_bound: Tuple[I64, U128, U64], cb, user_data=None, raw_data=False):
        lower_bound = Index128Object.generate_key_by_secondary(*lower_bound)
        upper_bound = Index128Object.generate_key_by_secondary(*upper_bound)
        return self.db.walk_range(index128_object_type, Index128Object.by_secondary, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(index128_object_type, Index128Object.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index128Object.unpack(dec)

    def lower_bound_by_primary(self, t_id: I64, primary_key: U64):
        lower_bound = Index128Object.generate_key_by_primary(t_id, primary_key)
        data = self.db.lower_bound(index128_object_type, Index128Object.by_primary, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index128Object.unpack(dec)

    def lower_bound_by_secondary(self, t_id: I64, secondary_key: U128, primary_key: U64):
        lower_bound = Index128Object.generate_key_by_secondary(t_id, secondary_key, primary_key)
        data = self.db.lower_bound(index128_object_type, Index128Object.by_secondary, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index128Object.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(index128_object_type, Index128Object.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index128Object.unpack(dec)

    def upper_bound_by_primary(self, t_id: I64, primary_key: U64):
        upper_bound = Index128Object.generate_key_by_primary(t_id, primary_key)
        data = self.db.upper_bound(index128_object_type, Index128Object.by_primary, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index128Object.unpack(dec)
    
    def upper_bound_by_secondary(self, t_id: I64, secondary_key: U128, primary_key: U64):
        upper_bound = Index128Object.generate_key_by_secondary(t_id, secondary_key, primary_key)
        data = self.db.upper_bound(index128_object_type, Index128Object.by_secondary, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index128Object.unpack(dec)

# index256_object_type = 10
class Index256ObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: Index256Object):
        enc = Encoder()
        obj.pack(enc)
        ret = self.db.create(index256_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(index256_object_type, Index256Object.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index256Object.unpack(dec)
    
    def find_by_primary(self, t_id: I64, primary_key: U64):
        key = i2b(t_id) + u2b(primary_key)
        data = self.db.find(index256_object_type, Index256Object.by_primary, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index256Object.unpack(dec)
    
    def find_by_secondary(self, t_id: I64, secondary_key: U256, primary_key: U64):
        key = i2b(t_id) + u2b(secondary_key, 32) + u2b(primary_key)
        data = self.db.find(index256_object_type, Index256Object.by_secondary, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index256Object.unpack(dec)

    def modify(self, perm: Index256Object):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(index256_object_type, Index256Object.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(index256_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = Index256Object.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index256_object_type, Index256Object.by_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_primary(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index256_object_type, Index256Object.by_primary, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_secondary(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index256_object_type, Index256Object.by_secondary, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(index256_object_type, Index256Object.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_primary(self, lower_bound: Tuple[I64, U64], upper_bound: Tuple[I64, U64], cb, user_data=None, raw_data=False):
        lower_bound = Index256Object.generate_key_by_primary(*lower_bound)
        upper_bound = Index256Object.generate_key_by_primary(*upper_bound)
        return self.db.walk_range(index256_object_type, Index256Object.by_primary, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_secondary(self, lower_bound: Tuple[I64, U256, U64], upper_bound: Tuple[I64, U256, U64], cb, user_data=None, raw_data=False):
        lower_bound = Index256Object.generate_key_by_secondary(*lower_bound)
        upper_bound = Index256Object.generate_key_by_secondary(*upper_bound)
        return self.db.walk_range(index256_object_type, Index256Object.by_secondary, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(index256_object_type, Index256Object.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index256Object.unpack(dec)

    def lower_bound_by_primary(self, t_id: I64, primary_key: U64):
        lower_bound = Index256Object.generate_key_by_primary(t_id, primary_key)
        data = self.db.lower_bound(index256_object_type, Index256Object.by_primary, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index256Object.unpack(dec)

    def lower_bound_by_secondary(self, t_id: I64, secondary_key: U256, primary_key: U64):
        lower_bound = Index256Object.generate_key_by_secondary(t_id, secondary_key, primary_key)
        data = self.db.lower_bound(index256_object_type, Index256Object.by_secondary, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index256Object.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(index256_object_type, Index256Object.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index256Object.unpack(dec)
    
    def upper_bound_by_primary(self, t_id: I64, primary_key: U64):
        upper_bound = Index256Object.generate_key_by_primary(t_id, primary_key)
        data = self.db.upper_bound(index256_object_type, Index256Object.by_primary, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index256Object.unpack(dec)
    
    def upper_bound_by_secondary(self, t_id: I64, secondary_key: U256, primary_key: U64):
        upper_bound = Index256Object.generate_key_by_secondary(t_id, secondary_key, primary_key)
        data = self.db.upper_bound(index256_object_type, Index256Object.by_secondary, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return Index256Object.unpack(dec)

# index_double_object_type = 11
class IndexDoubleObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: IndexDoubleObject):
        enc = Encoder()
        obj.pack(enc)
        ret = self.db.create(index_double_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(index_double_object_type, IndexDoubleObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return IndexDoubleObject.unpack(dec)
    
    def find_by_primary(self, t_id: I64, primary_key: U64):
        key = i2b(t_id) + u2b(primary_key)
        data = self.db.find(index_double_object_type, IndexDoubleObject.by_primary, key)
        if not data:
            return None
        dec = Decoder(data)
        return IndexDoubleObject.unpack(dec)

    def find_by_secondary(self, t_id: I64, secondary_key: F64, primary_key: U64):
        key = i2b(t_id) + f2b(secondary_key) + u2b(primary_key)
        data = self.db.find(index_double_object_type, IndexDoubleObject.by_secondary, key)
        if not data:
            return None
        dec = Decoder(data)
        return IndexDoubleObject.unpack(dec)

    def modify(self, perm: IndexDoubleObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(index_double_object_type, IndexDoubleObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(index_double_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = IndexDoubleObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index_double_object_type, IndexDoubleObject.by_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_primary(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index_double_object_type, IndexDoubleObject.by_primary, self.on_object_data, (cb, raw_data, user_data))
    
    def walk_by_secondary(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index_double_object_type, IndexDoubleObject.by_secondary, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(index_double_object_type, IndexDoubleObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_primary(self, lower_bound: Tuple[I64, U64], upper_bound: Tuple[I64, U64], cb, user_data=None, raw_data=False):
        lower_bound = IndexDoubleObject.generate_key_by_primary(*lower_bound)
        upper_bound = IndexDoubleObject.generate_key_by_primary(*upper_bound)
        return self.db.walk_range(index_double_object_type, IndexDoubleObject.by_primary, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_secondary(self, lower_bound: Tuple[I64, F64, U64], upper_bound: Tuple[I64, F64, U64], cb, user_data=None, raw_data=False):
        lower_bound = IndexDoubleObject.generate_key_by_secondary(*lower_bound)
        upper_bound = IndexDoubleObject.generate_key_by_secondary(*upper_bound)
        return self.db.walk_range(index_double_object_type, IndexDoubleObject.by_secondary, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(index_double_object_type, IndexDoubleObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexDoubleObject.unpack(dec)

    def lower_bound_by_primary(self, t_id: I64, primary_key: U64):
        lower_bound = IndexDoubleObject.generate_key_by_primary(t_id, primary_key)
        data = self.db.lower_bound(index_double_object_type, IndexDoubleObject.by_primary, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexDoubleObject.unpack(dec)
    
    def lower_bound_by_secondary(self, t_id: I64, secondary_key: F64, primary_key: U64):
        lower_bound = IndexDoubleObject.generate_key_by_secondary(t_id, secondary_key, primary_key)
        data = self.db.lower_bound(index_double_object_type, IndexDoubleObject.by_secondary, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexDoubleObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(index_double_object_type, IndexDoubleObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexDoubleObject.unpack(dec)
    
    def upper_bound_by_primary(self, t_id: I64, primary_key: U64):
        upper_bound = IndexDoubleObject.generate_key_by_primary(t_id, primary_key)
        data = self.db.upper_bound(index_double_object_type, IndexDoubleObject.by_primary, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexDoubleObject.unpack(dec)
    
    def upper_bound_by_secondary(self, t_id: I64, secondary_key: F64, primary_key: U64):
        upper_bound = IndexDoubleObject.generate_key_by_secondary(t_id, secondary_key, primary_key)
        data = self.db.upper_bound(index_double_object_type, IndexDoubleObject.by_secondary, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexDoubleObject.unpack(dec)

# index_long_double_object_type = 12
class IndexLongDoubleObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: IndexLongDoubleObject):
        enc = Encoder()
        obj.pack(enc)
        ret = self.db.create(index_long_double_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(index_long_double_object_type, IndexLongDoubleObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return IndexLongDoubleObject.unpack(dec)

    def find_by_primary(self, t_id: I64, primary_key: U64):
        key = i2b(t_id) + u2b(primary_key)
        data = self.db.find(index_long_double_object_type, IndexLongDoubleObject.by_primary, key)
        if not data:
            return None
        dec = Decoder(data)
        return IndexLongDoubleObject.unpack(dec)

    def find_by_secondary(self, t_id: I64, secondary_key: F128, primary_key: U64):
        key = i2b(t_id) + to_bytes(secondary_key) + u2b(primary_key)
        data = self.db.find(index_long_double_object_type, IndexLongDoubleObject.by_secondary, key)
        if not data:
            return None
        dec = Decoder(data)
        return IndexLongDoubleObject.unpack(dec)


    def modify(self, perm: IndexLongDoubleObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(index_long_double_object_type, IndexLongDoubleObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(index_long_double_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = IndexLongDoubleObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index_long_double_object_type, IndexLongDoubleObject.by_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_primary(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index_long_double_object_type, IndexLongDoubleObject.by_primary, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_secondary(self, cb, user_data=None, raw_data=False):
        return self.db.walk(index_long_double_object_type, IndexLongDoubleObject.by_secondary, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(index_long_double_object_type, IndexLongDoubleObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_primary(self, lower_bound: Tuple[I64, U64], upper_bound: Tuple[I64, U64], cb, user_data=None, raw_data=False):
        lower_bound = IndexLongDoubleObject.generate_key_by_primary(*lower_bound)
        upper_bound = IndexLongDoubleObject.generate_key_by_primary(*upper_bound)
        return self.db.walk_range(index_long_double_object_type, IndexLongDoubleObject.by_primary, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_secondary(self, lower_bound: Tuple[I64, F128, U64], upper_bound: Tuple[I64, F128, U64], cb, user_data=None, raw_data=False):
        lower_bound = IndexLongDoubleObject.generate_key_by_secondary(*lower_bound)
        upper_bound = IndexLongDoubleObject.generate_key_by_secondary(*upper_bound)
        return self.db.walk_range(index_long_double_object_type, IndexLongDoubleObject.by_secondary, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(index_long_double_object_type, IndexLongDoubleObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexLongDoubleObject.unpack(dec)

    def lower_bound_by_primary(self, t_id: I64, lower_bound: U64):
        lower_bound = IndexLongDoubleObject.generate_key_by_primary(t_id, lower_bound)
        data = self.db.lower_bound(index_long_double_object_type, IndexLongDoubleObject.by_primary, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexLongDoubleObject.unpack(dec)

    def lower_bound_by_secondary(self, t_id: I64, lower_bound: F128, primary_key: U64):
        lower_bound = IndexLongDoubleObject.generate_key_by_secondary(t_id, lower_bound, primary_key)
        data = self.db.lower_bound(index_long_double_object_type, IndexLongDoubleObject.by_secondary, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexLongDoubleObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(index_long_double_object_type, IndexLongDoubleObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexLongDoubleObject.unpack(dec)
    
    def upper_bound_by_primary(self, t_id: I64, primary_key: U64):
        upper_bound = IndexLongDoubleObject.generate_key_by_primary(t_id, primary_key)
        data = self.db.upper_bound(index_long_double_object_type, IndexLongDoubleObject.by_primary, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexLongDoubleObject.unpack(dec)
    
    def upper_bound_by_secondary(self, t_id: I64, secondary_key: F128, primary_key: U64):
        upper_bound = IndexLongDoubleObject.generate_key_by_secondary(t_id, secondary_key, primary_key)
        data = self.db.upper_bound(index_long_double_object_type, IndexLongDoubleObject.by_secondary, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return IndexLongDoubleObject.unpack(dec)

# global_property_object_type = 13
class GlobalPropertyObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, perm: GlobalPropertyObject):
        enc = Encoder()
        enc.pack(perm)
        ret = self.db.create(global_property_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def get(self):
        return self.find_by_id(0)

    def set(self, perm: GlobalPropertyObject):
        return self.modify(perm)

    def find(self):
        return self.find_by_id(0)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(global_property_object_type, GlobalPropertyObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return GlobalPropertyObject.unpack(dec)

    def modify(self, perm: GlobalPropertyObject):
        key = u2b(0)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(global_property_object_type, GlobalPropertyObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(global_property_object_type)

# dynamic_global_property_object_type = 14
class DynamicGlobalPropertyObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, perm: DynamicGlobalPropertyObject):
        enc = Encoder()
        enc.pack(perm)
        ret = self.db.create(dynamic_global_property_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def get(self):
        return self.find_by_id(0)

    def set(self, perm: DynamicGlobalPropertyObject):
        return self.modify(perm)

    def find(self):
        return self.find_by_id(0)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(dynamic_global_property_object_type, DynamicGlobalPropertyObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return DynamicGlobalPropertyObject.unpack(dec)

    def modify(self, perm: DynamicGlobalPropertyObject):
        key = u2b(0)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(dynamic_global_property_object_type, DynamicGlobalPropertyObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(dynamic_global_property_object_type)

# block_summary_object_type = 15
class BlockSummaryObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, perm: BlockSummaryObject):
        enc = Encoder()
        enc.pack(perm)
        ret = self.db.create(block_summary_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(block_summary_object_type, BlockSummaryObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return BlockSummaryObject.unpack(dec)
    
    def modify(self, perm: BlockSummaryObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(block_summary_object_type, BlockSummaryObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(block_summary_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = BlockSummaryObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(block_summary_object_type, BlockSummaryObject.by_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_block_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(block_summary_object_type, BlockSummaryObject.by_block_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(block_summary_object_type, BlockSummaryObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        return self.db.lower_bound(block_summary_object_type, BlockSummaryObject.by_id, lower_bound)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        return self.db.upper_bound(block_summary_object_type, BlockSummaryObject.by_id, upper_bound)

# transaction_object_type = 16
class TransactionObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, perm: TransactionObject):
        enc = Encoder()
        enc.pack(perm)
        ret = self.db.create(transaction_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(transaction_object_type, TransactionObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return TransactionObject.unpack(dec)

    def find_by_trx_id(self, trx_id: Checksum256):
        key = trx_id.to_bytes()
        data = self.db.find(transaction_object_type, TransactionObject.by_trx_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return TransactionObject.unpack(dec)
    
    def find_by_expiration(self, expiration: U32, table_id: I64):
        key = u2b(expiration, 4) + i2b(table_id)
        data = self.db.find(transaction_object_type, TransactionObject.by_expiration, key)
        if not data:
            return None
        dec = Decoder(data)
        return TransactionObject.unpack(dec)

    def modify(self, perm: TransactionObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(transaction_object_type, TransactionObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(transaction_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = TransactionObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(transaction_object_type, TransactionObject.by_id, self.on_object_data, (cb, raw_data, user_data))
    
    def walk_by_trx_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(transaction_object_type, TransactionObject.by_trx_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_expiration(self, cb, user_data=None, raw_data=False):
        return self.db.walk(transaction_object_type, TransactionObject.by_expiration, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(transaction_object_type, TransactionObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_trx_id(self, lower_bound: Checksum256, upper_bound: Checksum256, cb, user_data=None, raw_data=False):
        lower_bound = lower_bound.to_bytes()
        upper_bound = upper_bound.to_bytes()
        return self.db.walk_range(transaction_object_type, TransactionObject.by_trx_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_expiration(self, lower_bound: Union[U32, I64], upper_bound: Union[U32, I64], cb, user_data=None, raw_data=False):
        lower_bound = TransactionObject.generate_key_by_expiration(*lower_bound)
        upper_bound = TransactionObject.generate_key_by_expiration(*upper_bound)
        return self.db.walk_range(transaction_object_type, TransactionObject.by_expiration, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(transaction_object_type, TransactionObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return TransactionObject.unpack(dec)

    def lower_bound_by_trx_id(self, lower_bound: Checksum256):
        lower_bound = lower_bound.to_bytes()
        data = self.db.lower_bound(transaction_object_type, TransactionObject.by_trx_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return TransactionObject.unpack(dec)

    def lower_bound_by_expiration(self, expiration: U32, table_id: I64):
        lower_bound = TransactionObject.generate_key_by_expiration(expiration, table_id)
        data = self.db.lower_bound(transaction_object_type, TransactionObject.by_expiration, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return TransactionObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(transaction_object_type, TransactionObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return TransactionObject.unpack(dec)

    def upper_bound_by_trx_id(self, upper_bound: Checksum256):
        upper_bound = upper_bound.to_bytes()
        data = self.db.upper_bound(transaction_object_type, TransactionObject.by_trx_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return TransactionObject.unpack(dec)

    def upper_bound_by_expiration(self, expiration: U32, table_id: I64):
        upper_bound = TransactionObject.generate_key_by_expiration(expiration, table_id)
        data = self.db.upper_bound(transaction_object_type, TransactionObject.by_expiration, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return TransactionObject.unpack(dec)

# generated_transaction_object_type = 17
class GeneratedTransactionObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: GeneratedTransactionObject):
        enc = Encoder()
        obj.pack(enc)
        ret = self.db.create(generated_transaction_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(generated_transaction_object_type, GeneratedTransactionObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)

    def find_by_trx_id(self, trx_id: Union[str, Checksum256]):
        if isinstance(trx_id, str):
            trx_id = Checksum256.from_str(trx_id)
        assert isinstance(trx_id, Checksum256)
        data = self.db.find(generated_transaction_object_type, GeneratedTransactionObject.by_trx_id, trx_id.raw)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)

    def find_by_expiration(self, expiration: Union[I64, TimePoint], table_id: I64):
        key = GeneratedTransactionObject.generate_key_by_expiration(expiration, table_id)
        data = self.db.find(generated_transaction_object_type, GeneratedTransactionObject.by_expiration, key)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)
    
    def find_by_delay(self, delay: Union[I64, TimePoint], table_id: I64):
        key = GeneratedTransactionObject.generate_key_by_delay(delay, table_id)
        data = self.db.find(generated_transaction_object_type, GeneratedTransactionObject.by_delay, key)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)
    
    def find_by_sender_id(self, sender_id: I64, table_id: I64):
        key = GeneratedTransactionObject.generate_key_by_sender_id(sender_id, table_id)
        data = self.db.find(generated_transaction_object_type, GeneratedTransactionObject.by_sender_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)

    def modify(self, perm: GeneratedTransactionObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(generated_transaction_object_type, GeneratedTransactionObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(generated_transaction_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = GeneratedTransactionObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(generated_transaction_object_type, GeneratedTransactionObject.by_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_trx_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(generated_transaction_object_type, GeneratedTransactionObject.by_trx_id, self.on_object_data, (cb, raw_data, user_data))
    
    def walk_by_expiration(self, cb, user_data=None, raw_data=False):
        return self.db.walk(generated_transaction_object_type, GeneratedTransactionObject.by_expiration, self.on_object_data, (cb, raw_data, user_data))
    
    def walk_by_delay(self, cb, user_data=None, raw_data=False):
        return self.db.walk(generated_transaction_object_type, GeneratedTransactionObject.by_delay, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_sender_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(generated_transaction_object_type, GeneratedTransactionObject.by_sender_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(generated_transaction_object_type, GeneratedTransactionObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_trx_id(self, lower_bound: Union[bytes, Checksum256], upper_bound: Union[bytes, Checksum256], cb, user_data=None, raw_data=False):
        if isinstance(lower_bound, Checksum256):
            lower_bound = lower_bound.to_bytes()
        if isinstance(upper_bound, Checksum256):
            upper_bound = upper_bound.to_bytes()
        assert isinstance(lower_bound, bytes) and isinstance(upper_bound, bytes)
        assert len(lower_bound) == 32 and len(upper_bound) == 32
        return self.db.walk_range(generated_transaction_object_type, GeneratedTransactionObject.by_trx_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_expiration(self, lower_bound: Union[Union[I64, TimePoint], I64], upper_bound: Union[Union[I64, TimePoint], I64], cb, user_data=None, raw_data=False):
        lower_bound = GeneratedTransactionObject.generate_key_by_expiration(*lower_bound)
        upper_bound = GeneratedTransactionObject.generate_key_by_expiration(*upper_bound)
        return self.db.walk_range(generated_transaction_object_type, GeneratedTransactionObject.by_expiration, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_delay(self, lower_bound: Tuple[Union[I64, TimePoint], I64], upper_bound: Tuple[Union[I64, TimePoint], I64], cb, user_data=None, raw_data=False):
        lower_bound = GeneratedTransactionObject.generate_key_by_delay(*lower_bound)
        upper_bound = GeneratedTransactionObject.generate_key_by_delay(*upper_bound)
        return self.db.walk_range(generated_transaction_object_type, GeneratedTransactionObject.by_delay, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_sender_id(self, lower_bound: Tuple[Name, U128], upper_bound: Tuple[Name, U128], cb, user_data=None, raw_data=False):
        lower_bound = GeneratedTransactionObject.generate_key_by_sender_id(*lower_bound)
        upper_bound = GeneratedTransactionObject.generate_key_by_sender_id(*upper_bound)
        return self.db.walk_range(generated_transaction_object_type, GeneratedTransactionObject.by_sender_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(generated_transaction_object_type, GeneratedTransactionObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)

    def lower_bound_by_trx_id(self, lower_bound: Union[bytes, Checksum256]):
        if isinstance(lower_bound, Checksum256):
            lower_bound = lower_bound.to_bytes()
        assert isinstance(lower_bound, bytes)
        assert len(lower_bound) == 32

        data = self.db.lower_bound(generated_transaction_object_type, GeneratedTransactionObject.by_trx_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)
    
    def lower_bound_by_expiration(self, expiration: Union[I64, TimePoint], table_id: I64):
        lower_bound = GeneratedTransactionObject.generate_key_by_expiration(expiration, table_id)
        data = self.db.lower_bound(generated_transaction_object_type, GeneratedTransactionObject.by_expiration, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)
    
    def lower_bound_by_delay(self, delay_until: Union[I64, TimePoint], table_id: I64):
        lower_bound = GeneratedTransactionObject.generate_key_by_delay(delay_until, table_id)
        data = self.db.lower_bound(generated_transaction_object_type, GeneratedTransactionObject.by_delay, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)

    def lower_bound_by_sender_id(self, sender: Name, sender_id: U128):
        lower_bound = GeneratedTransactionObject.generate_key_by_sender_id(sender, sender_id)
        data = self.db.lower_bound(generated_transaction_object_type, GeneratedTransactionObject.by_sender_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(generated_transaction_object_type, GeneratedTransactionObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)

    def upper_bound_by_trx_id(self, upper_bound: Union[bytes, Checksum256]):
        if isinstance(upper_bound, Checksum256):
            upper_bound = upper_bound.to_bytes()
        assert isinstance(upper_bound, bytes)
        assert len(upper_bound) == 32

        data = self.db.upper_bound(generated_transaction_object_type, GeneratedTransactionObject.by_trx_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)
    
    def upper_bound_by_expiration(self, expiration: Union[I64, TimePoint], table_id: I64):
        upper_bound = GeneratedTransactionObject.generate_key_by_expiration(expiration, table_id)
        data = self.db.upper_bound(generated_transaction_object_type, GeneratedTransactionObject.by_expiration, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)
    
    def upper_bound_by_delay(self, delay_until: Union[I64, TimePoint], table_id: I64):
        upper_bound = GeneratedTransactionObject.generate_key_by_delay(delay_until, table_id)
        data = self.db.upper_bound(generated_transaction_object_type, GeneratedTransactionObject.by_delay, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)

    def upper_bound_by_sender_id(self, sender: Name, sender_id: U128):
        upper_bound = GeneratedTransactionObject.generate_key_by_sender_id(sender, sender_id)
        data = self.db.upper_bound(generated_transaction_object_type, GeneratedTransactionObject.by_sender_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)

# table_id_object_type = 30
class TableIdObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, perm: TableIdObject):
        enc = Encoder()
        perm.pack(enc)
        ret = self.db.create(table_id_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(table_id_object_type, TableIdObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return TableIdObject.unpack(dec)
    
    def find_by_code_scope_table(self, code: Name, scope: Name, table: Name):
        key = TableIdObject.generate_key_by_code_scope_table(code, scope, table)
        data = self.db.find(table_id_object_type, TableIdObject.by_code_scope_table, key)
        if not data:
            return None
        dec = Decoder(data)
        return TableIdObject.unpack(dec)

    def modify(self, perm: TableIdObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(table_id_object_type, TableIdObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(table_id_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = TableIdObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(table_id_object_type, TableIdObject.by_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_code_scope_table(self, cb, user_data=None, raw_data=False):
        return self.db.walk(table_id_object_type, TableIdObject.by_code_scope_table, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(table_id_object_type, TableIdObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_code_scope_table(self, lower_bound: Union[Name, Name, Name], upper_bound: Union[Name, Name, Name], cb, user_data=None, raw_data=False):
        lower_bound = TableIdObject.generate_key_by_code_scope_table(*lower_bound)
        upper_bound = TableIdObject.generate_key_by_code_scope_table(*upper_bound)
        return self.db.walk_range(table_id_object_type, TableIdObject.by_code_scope_table, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(table_id_object_type, TableIdObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return TableIdObject.unpack(dec)
    
    def lower_bound_by_code_scope_table(self, code: Name, scope: Name, table: Name):
        lower_bound = TableIdObject.generate_key_by_code_scope_table(code, scope, table)
        data = self.db.lower_bound(table_id_object_type, TableIdObject.by_code_scope_table, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return TableIdObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(table_id_object_type, TableIdObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return TableIdObject.unpack(dec)
    
    def upper_bound_by_code_scope_table(self, code: Name, scope: Name, table: Name):
        upper_bound = TableIdObject.generate_key_by_code_scope_table(code, scope, table)
        data = self.db.upper_bound(table_id_object_type, TableIdObject.by_code_scope_table, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return TableIdObject.unpack(dec)

# resource_limits_object_type = 31
class ResourceLimitsObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: ResourceLimitsObject):
        enc = Encoder()
        enc.pack(obj)
        ret = self.db.create(resource_limits_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(resource_limits_object_type, ResourceLimitsObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceLimitsObject.unpack(dec)
    
    def find_by_owner(self, pending: bool, owner: Name):
        key = ResourceLimitsObject.generate_key_by_owner(pending, owner)
        data = self.db.find(resource_limits_object_type, ResourceLimitsObject.by_owner, key)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceLimitsObject.unpack(dec)

    def modify(self, perm: ResourceLimitsObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(resource_limits_object_type, ResourceLimitsObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(resource_limits_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = ResourceLimitsObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(resource_limits_object_type, ResourceLimitsObject.by_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_owner(self, cb, user_data=None, raw_data=False):
        return self.db.walk(resource_limits_object_type, ResourceLimitsObject.by_owner, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(resource_limits_object_type, ResourceLimitsObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_owner(self, lower_bound: Tuple[bool, Name], upper_bound: Tuple[bool, Name], cb, user_data=None, raw_data=False):
        lower_bound = ResourceLimitsObject.generate_key_by_owner(*lower_bound)
        upper_bound = ResourceLimitsObject.generate_key_by_owner(*upper_bound)
        return self.db.walk_range(resource_limits_object_type, ResourceLimitsObject.by_owner, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(resource_limits_object_type, ResourceLimitsObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceLimitsObject.unpack(dec)

    def lower_bound_by_owner(self, pending: bool, owner: Name):
        lower_bound = ResourceLimitsObject.generate_key_by_owner(pending, owner)
        data = self.db.lower_bound(resource_limits_object_type, ResourceLimitsObject.by_owner, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceLimitsObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(resource_limits_object_type, ResourceLimitsObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceLimitsObject.unpack(dec)
    
    def upper_bound_by_owner(self, pending: bool, owner: Name):
        upper_bound = ResourceLimitsObject.generate_key_by_owner(pending, owner)
        data = self.db.upper_bound(resource_limits_object_type, ResourceLimitsObject.by_owner, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceLimitsObject.unpack(dec)

# resource_usage_object_type = 32
class ResourceUsageObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: ResourceUsageObject):
        enc = Encoder()
        enc.pack(obj)
        ret = self.db.create(resource_usage_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(resource_usage_object_type, ResourceUsageObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceUsageObject.unpack(dec)
    
    def find_by_owner(self, owner: Name):
        key = eos.s2b(owner)
        data = self.db.find(resource_usage_object_type, ResourceUsageObject.by_owner, key)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceUsageObject.unpack(dec)

    def modify(self, perm: ResourceUsageObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(resource_usage_object_type, ResourceUsageObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(resource_usage_object_type)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = ResourceUsageObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(resource_usage_object_type, ResourceUsageObject.by_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_owner(self, cb, user_data=None, raw_data=False):
        return self.db.walk(resource_usage_object_type, ResourceUsageObject.by_owner, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, lower_bound: I64, upper_bound: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(lower_bound)
        upper_bound = i2b(upper_bound)
        return self.db.walk_range(resource_usage_object_type, ResourceUsageObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_owner(self, lower_bound: Name, upper_bound: Name, cb, user_data=None, raw_data=False):
        lower_bound = eos.s2b(lower_bound)
        upper_bound = eos.s2b(upper_bound)
        return self.db.walk_range(resource_usage_object_type, ResourceUsageObject.by_owner, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, lower_bound: I64):
        lower_bound = i2b(lower_bound)
        data = self.db.lower_bound(resource_usage_object_type, ResourceUsageObject.by_id, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceUsageObject.unpack(dec)

    def lower_bound_by_owner(self, lower_bound: Name):
        lower_bound = eos.s2b(lower_bound)
        data = self.db.lower_bound(resource_usage_object_type, ResourceUsageObject.by_owner, lower_bound)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceUsageObject.unpack(dec)

    def upper_bound_by_id(self, upper_bound: I64):
        upper_bound = i2b(upper_bound)
        data = self.db.upper_bound(resource_usage_object_type, ResourceUsageObject.by_id, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceUsageObject.unpack(dec)
    
    def upper_bound_by_owner(self, upper_bound: Name):
        upper_bound = eos.s2b(upper_bound)
        data = self.db.upper_bound(resource_usage_object_type, ResourceUsageObject.by_owner, upper_bound)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceUsageObject.unpack(dec)

# resource_limits_state_object_type = 33
class ResourceLimitsStateObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: ResourceLimitsStateObject):
        enc = Encoder()
        enc.pack(obj)
        ret = self.db.create(resource_limits_state_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def get(self):
        return self.find_by_id(0)

    def set(self, perm: ResourceLimitsStateObject):
        return self.modify(perm)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(resource_limits_state_object_type, ResourceLimitsStateObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceLimitsStateObject.unpack(dec)

    def modify(self, perm: ResourceLimitsStateObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(resource_limits_state_object_type, ResourceLimitsStateObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(resource_limits_state_object_type)

# resource_limits_config_object_type = 34
class ResourceLimitsConfigObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: ResourceLimitsConfigObject):
        enc = Encoder()
        enc.pack(obj)
        ret = self.db.create(resource_limits_config_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def get(self):
        return self.find_by_id(0)

    def set(self, perm: ResourceLimitsConfigObject):
        return self.modify(perm)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(resource_limits_config_object_type, ResourceLimitsConfigObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceLimitsConfigObject.unpack(dec)

    def modify(self, perm: ResourceLimitsConfigObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(resource_limits_config_object_type, ResourceLimitsConfigObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(resource_limits_config_object_type)

# protocol_state_object_type = 38
class ProtocolStateObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: ProtocolStateObject):
        enc = Encoder()
        enc.pack(obj)
        ret = self.db.create(protocol_state_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def get(self):
        return self.find_by_id(0)

    def set(self, perm: ProtocolStateObject):
        return self.modify(perm)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(protocol_state_object_type, ProtocolStateObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return ProtocolStateObject.unpack(dec)

    def modify(self, perm: ProtocolStateObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(protocol_state_object_type, ProtocolStateObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(protocol_state_object_type)

# account_ram_correction_object_type = 39
class AccountRamCorrectionObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: AccountRamCorrectionObject):
        enc = Encoder()
        enc.pack(obj)
        ret = self.db.create(account_ram_correction_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(account_ram_correction_object_type, AccountRamCorrectionObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return AccountRamCorrectionObject.unpack(dec)

    def modify(self, perm: AccountRamCorrectionObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(account_ram_correction_object_type, AccountRamCorrectionObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(account_ram_correction_object_type)

# code_object_type = 40
class CodeObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, obj: CodeObject):
        enc = Encoder()
        enc.pack(obj)
        ret = self.db.create(code_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.find(code_object_type, CodeObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return CodeObject.unpack(dec)

    def convert_code_hash(self, code_hash: Union[str, bytes, Checksum256]):
        if isinstance(code_hash, str):
            code_hash = Checksum256.from_str(code_hash).to_bytes()
        elif isinstance(code_hash, Checksum256):
            code_hash = code_hash.to_bytes()
        assert isinstance(code_hash, bytes)
        assert len(code_hash) == 32, 'code_hash must be 32 bytes'
        return code_hash

    def find_by_code_hash(self, code_hash: Union[str, bytes, Checksum256], vm_type: U8, vm_version: U8):
        code_hash = self.convert_code_hash(code_hash)
        key = code_hash + u2b(vm_type, 1) + u2b(vm_version, 1)
        data = self.db.find(code_object_type, CodeObject.by_code_hash, key)
        if not data:
            return None
        dec = Decoder(data)
        return CodeObject.unpack(dec)

    def on_object_data(self, tp, data, custom_data):
        cb, raw_data, user_data = custom_data
        if raw_data:
            return cb(data, user_data)
        dec = Decoder(data)
        obj = CodeObject.unpack(dec)
        return cb(obj, user_data)

    def walk_by_id(self, cb, user_data=None, raw_data=False):
        return self.db.walk(database.code_object_type, CodeObject.by_id, self.on_object_data, (cb, raw_data, user_data))

    def walk_by_code_hash(self, cb, user_data=None, raw_data=False):
        return self.db.walk(database.code_object_type, CodeObject.by_code_hash, self.on_object_data, (cb, raw_data, user_data))

    def walk_range_by_id(self, start_id: I64, end_id: I64, cb, user_data=None, raw_data=False):
        lower_bound = i2b(start_id)
        upper_bound = i2b(end_id)
        return self.db.walk_range(database.code_object_type, CodeObject.by_id, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def convert_by_code_hash_key(self, key: Tuple[Union[str, bytes, Checksum256], U8, U8]):
        code_hash, vm_type, vm_version = key
        return self.convert_code_hash(code_hash) + u2b(vm_type) + u2b(vm_version, 1)

    def walk_range_by_code_hash(self, lower_bound: Tuple[Union[str, bytes, Checksum256], U8, U8], upper_bound: Tuple[Union[str, bytes, Checksum256], U8, U8], cb, user_data=None, raw_data=False):
        lower_bound = self.convert_by_code_hash_key(lower_bound)
        upper_bound = self.convert_by_code_hash_key(upper_bound)
        return self.db.walk_range(database.code_object_type, CodeObject.by_code_hash, lower_bound, upper_bound, self.on_object_data, (cb, raw_data, user_data))

    def lower_bound_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.lower_bound(code_object_type, CodeObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return CodeObject.unpack(dec)

    def lower_bound_by_code_hash(self, lower_bound: Tuple[Union[str, bytes, Checksum256], U8, U8]):
        key = self.convert_by_code_hash_key(lower_bound)
        data = self.db.lower_bound(code_object_type, CodeObject.by_code_hash, key)
        if not data:
            return None
        dec = Decoder(data)
        return CodeObject.unpack(dec)

    def upper_bound_by_id(self, table_id: I64):
        key = i2b(table_id)
        data = self.db.upper_bound(code_object_type, CodeObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return CodeObject.unpack(dec)

    def upper_bound_by_code_hash(self, upper_bound: Tuple[Union[str, bytes, Checksum256], U8, U8]):
        key = self.convert_by_code_hash_key(upper_bound)
        data = self.db.upper_bound(code_object_type, CodeObject.by_code_hash, key)
        if not data:
            return None
        dec = Decoder(data)
        return CodeObject.unpack(dec)

    def modify(self, perm: CodeObject):
        key = i2b(perm.table_id)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(code_object_type, CodeObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(code_object_type)

# database_header_object_type = 41
class DatabaseHeaderObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def create(self, perm: DatabaseHeaderObject):
        enc = Encoder()
        enc.pack(perm)
        ret = self.db.create(database_header_object_type, enc.get_bytes())
        return parse_return_value(ret)

    def get(self):
        return self.find_by_id(0)

    def set(self, perm: DatabaseHeaderObject):
        return self.modify(perm)

    def find(self, table_id=0):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id=0):
        key = i2b(table_id)
        data = self.db.find(database_header_object_type, DatabaseHeaderObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return DatabaseHeaderObject.unpack(dec)

    def modify(self, perm: DatabaseHeaderObject):
        key = u2b(0)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(database_header_object_type, DatabaseHeaderObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(database_header_object_type)

def new(db_ptr: int = 0):
    return Database(db_ptr)

def new_ex(state_dir: str, shared_file_size: U64, read_only: bool = True, allow_dirty: bool = True):
    ptr = _database.new_database(state_dir, read_only, shared_file_size, allow_dirty)
    if ptr == 0:
        raise get_last_exception()
    return Database(ptr, False)
