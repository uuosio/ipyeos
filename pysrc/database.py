from typing import Union

from . import _database
from . import _eos
from .types import U8, U16, U32, U64, I64, Name, Checksum256
from .packer import Encoder, Decoder
from .database_objects import *

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
      
class Database:
    def __init__(self, db_ptr: int = 0):
        if not db_ptr:
            # default to get db ptr from chain_plugin.chain.db()
            self.db_ptr = _eos.get_database()
        else:
            self.db_ptr = db_ptr
        self.ptr = _database.new()

    def modify(self, tp: int, index_position: int, raw_key: bytes, raw_data: bytes):
        ret = _database.modify(self.ptr, self.db_ptr, tp, index_position, raw_key, raw_data)
        if ret == -2:
            raise Exception(_eos.get_last_error_and_clear())
        assert ret in (0, 1)
        if ret:
            return True
        return False

    def walk(self, tp: int, index_position: int, cb, custom_data = None):
        ret = _database.walk(self.ptr, self.db_ptr, tp, index_position, cb, custom_data)
        if ret == -2:
            raise Exception(_eos.get_last_error_and_clear())
        return ret

    def walk_range(self, tp: int, index_position: int, lower_bound: Union[int, bytes], upper_bound: Union[int, bytes], cb, custom_data = None):
        if index_position == 0:
            if isinstance(lower_bound, int):
                lower_bound = int.to_bytes(lower_bound, 8, 'little')
            if isinstance(upper_bound, int):
                upper_bound = int.to_bytes(upper_bound, 8, 'little')

        ret = _database.walk_range(self.ptr, self.db_ptr, tp, index_position, lower_bound, upper_bound, cb, custom_data)
        if ret == -2:
            raise Exception(_eos.get_last_error_and_clear())
        return ret

    def find(self, tp: int, index_position: int, key: Union[int, bytes]):
        if index_position == 0 and isinstance(key, int):
            key = int.to_bytes(key, 8, 'little')
        ret, data = _database.find(self.ptr, self.db_ptr, tp, index_position, key)
        if ret == -2:
            raise Exception(_eos.get_last_error_and_clear())
        if ret == 0:
            return None
        return data

    def lower_bound(self, tp: int, index_position: int, key: Union[int, bytes]):
        if index_position == 0 and isinstance(key, int):
            key = int.to_bytes(key, 8, 'little')
        ret, data = _database.lower_bound(self.ptr, self.db_ptr, tp, index_position, key)
        if ret == -2:
            raise Exception(_eos.get_last_error_and_clear())
        if ret == 0:
            return None
        return data

    def upper_bound(self, tp: int, index_position: int, key: Union[int, bytes]):
        if index_position == 0 and isinstance(key, int):
            key = int.to_bytes(key, 8, 'little')

        ret, data = _database.upper_bound(self.ptr, self.db_ptr, tp, index_position, key)
        if ret == -2:
            raise Exception(_eos.get_last_error_and_clear())
        if ret == 0:
            return None
        return data

    def row_count(self, tp: int):
        ret = _database.row_count(self.ptr, self.db_ptr, tp)
        if ret == -2:
            raise Exception(f"invalid database object type: {tp}")
        return ret

# account_object_type = 1
class AccountObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
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

    def modify(self, perm: AccountObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(account_object_type, AccountObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(account_object_type)

# account_metadata_object_type = 2
class AccountMetadataObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(account_metadata_object_type, AccountMetadataObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return AccountMetadataObject.unpack(dec)

    def modify(self, perm: AccountMetadataObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(account_metadata_object_type, AccountMetadataObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(account_metadata_object_type)

# permission_object_type = 3
class PermissionObjectIndex(object):
    
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
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
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(permission_object_type, PermissionObject.by_id, key, enc.get_bytes())

# permission_usage_object_type = 4
class PermissionUsageObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(permission_usage_object_type, PermissionUsageObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionUsageObject.unpack(dec)

    def modify(self, perm: PermissionUsageObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(permission_usage_object_type, PermissionUsageObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(permission_usage_object_type)

# permission_link_object_type = 5
class PermissionLinkObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(permission_link_object_type, PermissionLinkObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return PermissionLinkObject.unpack(dec)

    def modify(self, perm: PermissionLinkObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(permission_link_object_type, PermissionLinkObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(permission_link_object_type)

# key_value_object_type = 7
class KeyValueObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(key_value_object_type, KeyValueObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return KeyValueObject.unpack(dec)

    def modify(self, perm: KeyValueObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(key_value_object_type, KeyValueObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(key_value_object_type)

# index64_object_type = 8
class Index64ObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(index64_object_type, Index64Object.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index64Object.unpack(dec)

    def modify(self, perm: Index64Object):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(index64_object_type, Index64Object.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(index64_object_type)

# index128_object_type = 9
class Index128ObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(index128_object_type, Index128Object.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index128Object.unpack(dec)

    def modify(self, perm: Index128Object):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(index128_object_type, Index128Object.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(index128_object_type)

# index256_object_type = 10
class Index256ObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(index256_object_type, Index256Object.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return Index256Object.unpack(dec)

    def modify(self, perm: Index256Object):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(index256_object_type, Index256Object.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(index256_object_type)

# index_double_object_type = 11
class IndexDoubleObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(index_double_object_type, IndexDoubleObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return IndexDoubleObject.unpack(dec)

    def modify(self, perm: IndexDoubleObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(index_double_object_type, IndexDoubleObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(index_double_object_type)

# index_long_double_object_type = 12
class IndexLongDoubleObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(index_long_double_object_type, IndexLongDoubleObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return IndexLongDoubleObject.unpack(dec)

    def modify(self, perm: IndexLongDoubleObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(index_long_double_object_type, IndexLongDoubleObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(index_long_double_object_type)

# global_property_object_type = 13
class GlobalPropertyObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self):
        return self.find_by_id(0)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(global_property_object_type, GlobalPropertyObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return GlobalPropertyObject.unpack(dec)

    def modify(self, perm: GlobalPropertyObject):
        key = int.to_bytes(0, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(global_property_object_type, GlobalPropertyObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(global_property_object_type)

# dynamic_global_property_object_type = 14
class DynamicGlobalPropertyObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self):
        return self.find_by_id(0)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(dynamic_global_property_object_type, DynamicGlobalPropertyObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return DynamicGlobalPropertyObject.unpack(dec)

    def modify(self, perm: DynamicGlobalPropertyObject):
        key = int.to_bytes(0, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(dynamic_global_property_object_type, DynamicGlobalPropertyObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(dynamic_global_property_object_type)

# block_summary_object_type = 15
class BlockSummaryObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(block_summary_object_type, BlockSummaryObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return BlockSummaryObject.unpack(dec)

    def modify(self, perm: BlockSummaryObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(block_summary_object_type, BlockSummaryObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(block_summary_object_type)

# transaction_object_type = 16
class TransactionObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(transaction_object_type, TransactionObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return TransactionObject.unpack(dec)

    def modify(self, perm: TransactionObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(transaction_object_type, TransactionObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(transaction_object_type)

# generated_transaction_object_type = 17
class GeneratedTransactionObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
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

    def find_by_expiration(self, expiration: I64):
        key = int.to_bytes(expiration, 8, 'little', signed=True)
        data = self.db.find(generated_transaction_object_type, GeneratedTransactionObject.by_expiration, key)
        if not data:
            return None
        dec = Decoder(data)
        return GeneratedTransactionObject.unpack(dec)

    def walk_by_expiration(self, cb):
        self.db.walk(generated_transaction_object_type, GeneratedTransactionObject.by_expiration, cb)

    def modify(self, perm: GeneratedTransactionObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(generated_transaction_object_type, GeneratedTransactionObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(generated_transaction_object_type)

# table_id_object_type = 30
class TableIdObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(table_id_object_type, TableIdObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return TableIdObject.unpack(dec)

    def modify(self, perm: TableIdObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(table_id_object_type, TableIdObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(table_id_object_type)

# resource_limits_object_type = 31
class ResourceLimitsObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(resource_limits_object_type, ResourceLimitsObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceLimitsObject.unpack(dec)

    def modify(self, perm: ResourceLimitsObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(resource_limits_object_type, ResourceLimitsObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(resource_limits_object_type)
# resource_usage_object_type = 32
class ResourceUsageObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(resource_usage_object_type, ResourceUsageObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceUsageObject.unpack(dec)

    def modify(self, perm: ResourceUsageObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(resource_usage_object_type, ResourceUsageObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(resource_usage_object_type)

# resource_limits_state_object_type = 33
class ResourceLimitsStateObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(resource_limits_state_object_type, ResourceLimitsStateObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceLimitsStateObject.unpack(dec)

    def modify(self, perm: ResourceLimitsStateObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(resource_limits_state_object_type, ResourceLimitsStateObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(resource_limits_state_object_type)

# resource_limits_config_object_type = 34
class ResourceLimitsConfigObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(resource_limits_config_object_type, ResourceLimitsConfigObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return ResourceLimitsConfigObject.unpack(dec)

    def modify(self, perm: ResourceLimitsConfigObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(resource_limits_config_object_type, ResourceLimitsConfigObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(resource_limits_config_object_type)

# protocol_state_object_type = 38
class ProtocolStateObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(protocol_state_object_type, ProtocolStateObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return ProtocolStateObject.unpack(dec)

    def modify(self, perm: ProtocolStateObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(protocol_state_object_type, ProtocolStateObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(protocol_state_object_type)

# account_ram_correction_object_type = 39
class AccountRamCorrectionObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(account_ram_correction_object_type, AccountRamCorrectionObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return AccountRamCorrectionObject.unpack(dec)

    def modify(self, perm: AccountRamCorrectionObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(account_ram_correction_object_type, AccountRamCorrectionObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(account_ram_correction_object_type)

# code_object_type = 40
class CodeObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id: I64):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id: I64):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(code_object_type, CodeObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return CodeObject.unpack(dec)

    def find_by_code_hash(self, code_hash: Union[str, bytes, Checksum256], vm_type: U8, vm_version: U8):
        if isinstance(code_hash, str):
            code_hash = Checksum256.from_str(code_hash).get_bytes()
        elif isinstance(code_hash, Checksum256):
            code_hash = code_hash.get_bytes()
        assert isinstance(code_hash, bytes)
        assert len(code_hash) == 32, 'code_hash must be 32 bytes'
        key = code_hash + int.to_bytes(vm_type, 1, 'little') + int.to_bytes(vm_version, 1, 'little')
        data = self.db.find(code_object_type, CodeObject.by_code_hash, key)
        if not data:
            return None
        dec = Decoder(data)
        return CodeObject.unpack(dec)

    def modify(self, perm: CodeObject):
        key = int.to_bytes(perm.table_id, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(code_object_type, CodeObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(code_object_type)

# database_header_object_type = 41
class DatabaseHeaderObjectIndex(object):
    def __init__(self, db: Database):
        self.db = db

    def find(self, table_id=0):
        return self.find_by_id(table_id)

    def find_by_id(self, table_id=0):
        key = int.to_bytes(table_id, 8, 'little', signed=True)
        data = self.db.find(database_header_object_type, DatabaseHeaderObject.by_id, key)
        if not data:
            return None
        dec = Decoder(data)
        return DatabaseHeaderObject.unpack(dec)

    def modify(self, perm: DatabaseHeaderObject):
        key = int.to_bytes(0, 8, 'little', signed=True)
        enc = Encoder()
        enc.pack(perm)
        return self.db.modify(database_header_object_type, DatabaseHeaderObject.by_id, key, enc.get_bytes())

    def row_count(self):
        return self.db.row_count(database_header_object_type)
