import hashlib
from typing import Generic, List, NewType, Optional, TypeVar, Union

from . import database, eos
from .packer import Decoder, Encoder
from .structs import (Authority, KeyWeight, PermissionLevel,
                      PermissionLevelWeight, TimePoint, Variant, WaitWeight)
from .types import (F128, I64, U8, U16, U32, U64, U128, U256, Checksum256,
                    Name, PublicKey, TimePointSec)
from .utils import f2b, i2b, to_bytes, u2b

# struct account_object_ {
#     account_name         name; //< name should not be changed within a chainbase modifier lambda
#     block_timestamp_type creation_date;
#     vector<char>          abi;
# };

class template(object):
    def __init__(self):
        pass

    def __repr__(self):
        pass

    def __eq__(self, other):
        pass

    def pack(self, enc: Encoder) -> int:
        pass

    @classmethod
    def unpack(cls, dec: Decoder):
        pass

class AccountObject(object):
    by_id = 0
    by_name = 1
    def __init__(self, table_id: I64, name: Name, creation_date: U32, abi: bytes):
        self._table_id = table_id
        self.name = name
        self.creation_date = creation_date
        self.abi = abi

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{name: {self.name}, creation_date: {self.creation_date}, abi: {self.abi}}}"

    def __eq__(self, other):
        return self.name == other.name \
            and self.creation_date == other.creation_date \
            and self.abi == other.abi

    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack_name(self.name)
        enc.pack_u32(self.creation_date)
        enc.pack_bytes(self.abi)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        name = dec.unpack_name()
        creation_date = dec.unpack_u32()
        abi = dec.unpack_bytes()
        return AccountObject(table_id, name, creation_date, abi)

# struct account_metadata_object_
# {
#     account_name          name; //< name should not be changed within a chainbase modifier lambda
#     uint64_t              recv_sequence = 0;
#     uint64_t              auth_sequence = 0;
#     uint64_t              code_sequence = 0;
#     uint64_t              abi_sequence  = 0;
#     digest_type           code_hash;
#     time_point            last_code_update;
#     uint32_t              flags = 0;
#     uint8_t               vm_type = 0;
#     uint8_t               vm_version = 0;
# };

class AccountMetadataObject(object):
    by_id = 0
    by_name = 1
    def __init__(self, table_id: I64, name: Name, recv_sequence: U64, auth_sequence: U64, code_sequence: U64, abi_sequence: U64, \
                code_hash: Checksum256, last_code_update: I64, flags: U32, vm_type: U8, vm_version: U8):
        self._table_id = table_id
        self.name = name
        self.recv_sequence = recv_sequence
        self.auth_sequence = auth_sequence
        self.code_sequence = code_sequence
        self.abi_sequence = abi_sequence
        self.code_hash = code_hash
        self.last_code_update = last_code_update
        self.flags = flags
        self.vm_type = vm_type
        self.vm_version = vm_version

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{name: {self.name}, recv_sequence: {self.recv_sequence}, \
        auth_sequence: {self.auth_sequence}, \
        code_sequence: {self.code_sequence}, \
        abi_sequence: {self.abi_sequence}, \
        code_hash: {self.code_hash}, \
        last_code_update: {self.last_code_update}, \
        flags: self.last_code_update, \
        vm_type: {self.vm_type}, \
        vm_version: {self.vm_version}}}"

    def __eq__(self, other):
        return self.name == self.name \
        and self.recv_sequence == other.recv_sequence \
        and self.auth_sequence == other.auth_sequence \
        and self.code_sequence == other.code_sequence \
        and self.abi_sequence == other.abi_sequence \
        and self.code_hash == other.code_hash \
        and self.last_code_update == other.last_code_update \
        and self.flags == other.flags \
        and self.vm_type == other.vm_type \
        and self.vm_version == other.vm_version

    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack_name(self.name)
        enc.pack_u64(self.recv_sequence)
        enc.pack_u64(self.auth_sequence)
        enc.pack_u64(self.code_sequence)
        enc.pack_u64(self.abi_sequence)
        enc.pack_checksum256(self.code_hash)
        enc.pack_i64(self.last_code_update)
        enc.pack_u32(self.flags)
        enc.pack_u8(self.vm_type)
        enc.pack_u8(self.vm_version)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        name = dec.unpack_name()
        recv_sequence = dec.unpack_u64()
        auth_sequence = dec.unpack_u64()
        code_sequence = dec.unpack_u64()
        abi_sequence = dec.unpack_u64()
        code_hash = dec.unpack_checksum256()
        last_code_update = dec.unpack_i64()
        flags = dec.unpack_u32()
        vm_type = dec.unpack_u8()
        vm_version = dec.unpack_u8()
        return AccountMetadataObject(table_id, name, recv_sequence, auth_sequence, code_sequence, abi_sequence, \
            code_hash, last_code_update, flags, vm_type, vm_version)

# struct permission_object_ {
#     permission_usage_object::id_type  usage_id;
#     int64_t                           parent; ///< parent permission
#     account_name                      owner; ///< the account this permission belongs to (should not be changed within a chainbase modifier lambda)
#     permission_name                   name; ///< human-readable name for the permission (should not be changed within a chainbase modifier lambda)
#     time_point                        last_updated; ///< the last time this authority was updated
#     authority                         auth; ///< authority required to execute this permission
# };

#   permission_usage_object::id_type  usage_id;
#   id_type                           parent; ///< parent permission
#   account_name                      owner; ///< the account this permission belongs to (should not be changed within a chainbase modifier lambda)
#   permission_name                   name; ///< human-readable name for the permission (should not be changed within a chainbase modifier lambda)
#   time_point                        last_updated; ///< the last time this authority was updated
#   shared_authority                  auth; ///< authority required to execute this permission
#       threshold
#       shared_vector<shared_key_weight>           keys;
#           shared_public_key key;
#           weight_type       weight;
#       shared_vector<permission_level_weight>     accounts;
#           permission_level  permission;
#           weight_type       weight;
#       shared_vector<wait_weight>                 waits;
#           uint32_t     wait_sec;
#           weight_type  weight;

class PermissionObject(object):
    """
    by_parent: permission_object::parent permission_object::id
    by_owner:  permission_object::owner permission_object::name
    by_name:   permission_object::name permission_object::id
    """
    by_id = 0
    by_parent = 1
    by_owner = 2
    by_name = 3

    def __init__(self, table_id: I64, usage_id: I64, parent: I64, owner: Name, name: Name, last_updated: I64, auth: Authority):
        self._table_id = table_id
        self.usage_id = usage_id
        self.parent = parent
        self.owner = owner
        self.name = name
        self.last_updated = last_updated
        self.auth = auth

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{table_id: {self.table_id}, usage_id: {self.usage_id}, parent: {self.parent}, owner: {self.owner}, name: {self.name}, last_updated: {self.last_updated}, auth: {self.auth}}}"

    def __eq__(self, other) -> bool:
        return self.usage_id == other.usage_id \
            and self.parent == other.parent \
            and self.owner == other.owner \
            and self.name == other.name \
            and self.last_updated == other.last_updated \
            and self.auth == other.auth

    @classmethod
    def generate_key_by_id(cls, table_id: I64):
        return i2b(table_id)

    @classmethod
    def generate_key_by_parent(cls, parent: I64, table_id: I64):
        return i2b(parent) + i2b(table_id)

    @classmethod
    def generate_key_by_owner(cls, owner: Name, name: Name):
        return eos.s2b(owner) + eos.s2b(name)

    @classmethod
    def generate_key_by_name(cls, name: Name, table_id: I64):
        return eos.s2b(name) + i2b(table_id)

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_i64(self.usage_id)
        enc.pack_i64(self.parent)
        enc.pack_name(self.owner)
        enc.pack_name(self.name)
        enc.pack_i64(self.last_updated)
        enc.pack(self.auth)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
    #   permission_usage_object::id_type  usage_id;
    #   id_type                           parent; ///< parent permission
    #   account_name                      owner; ///< the account this permission belongs to (should not be changed within a chainbase modifier lambda)
    #   permission_name                   name; ///< human-readable name for the permission (should not be changed within a chainbase modifier lambda)
    #   time_point                        last_updated; ///< the last time this authority was updated
        table_id = dec.unpack_i64()
        usage_id = dec.unpack_i64()
        parent = dec.unpack_i64()
        owner = dec.unpack_name()
        name = dec.unpack_name()
        last_updated = dec.unpack_i64()
        auth = Authority.unpack(dec)
        return PermissionObject(table_id, usage_id, parent, owner, name, last_updated, auth)

# struct permission_usage_object_ {
#     time_point        last_used;   ///< when this permission was last used
# };

class PermissionUsageObject(object):
    by_id = 0
    def __init__(self, table_id: I64, last_used: I64):
        self._table_id = table_id
        self.last_used = last_used

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{last_used: {self.last_used}}}"

    def __eq__(self, other):
        return self.last_used == other.last_used

    def pack(self, enc: Encoder) -> int:
        return enc.pack_i64(self.last_used)

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        last_used = dec.unpack_i64()
        return PermissionUsageObject(table_id, last_used)

# struct permission_link_object_ {
#     /// The account which is defining its permission requirements
#     account_name    account;
#     /// The contract which account requires @ref required_permission to invoke
#     account_name    code; /// TODO: rename to scope
#     /// The message type which account requires @ref required_permission to invoke
#     /// May be empty; if so, it sets a default @ref required_permission for all messages to @ref code
#     action_name       message_type;
#     /// The permission level which @ref account requires for the specified message types
#     /// all of the above fields should not be changed within a chainbase modifier lambda
#     permission_name required_permission;
# };

class PermissionLinkObject(object):
    by_id = 0
    by_action_name = 1
    by_permission_name = 2
    def __init__(self, table_id: I64, account: Name, code: Name, message_type: Name, required_permission: Name):
        self._table_id = table_id
        self.account = account
        self.code = code
        self.message_type = message_type
        self.required_permission = required_permission
    
    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{account: {self.account}, code: {self.code}, message_type: {self.message_type}, required_permission: {self.required_permission}}}"
    
    def __eq__(self, other):
        return self.account == other.account \
            and self.code == other.code \
            and self.message_type == other.message_type \
            and self.required_permission == other.required_permission
    
    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_name(self.account)
        enc.pack_name(self.code)
        enc.pack_name(self.message_type)
        enc.pack_name(self.required_permission)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        account = dec.unpack_name()
        code = dec.unpack_name()
        message_type = dec.unpack_name()
        required_permission = dec.unpack_name()
        return PermissionLinkObject(table_id, account, code, message_type, required_permission)

    @classmethod
    def generate_key_by_action_name(cls, account: Name, code: Name, message_type: Name):
        return eos.s2b(account) + eos.s2b(code) + eos.s2b(message_type)
    
    @classmethod
    def generate_key_by_permission_name(cls, account: Name, required_permission: Name, table_id: I64):
        return eos.s2b(account) + eos.s2b(required_permission) + i2b(table_id)


# struct key_value_object_ {
#     int64_t              t_id; //< t_id should not be changed within a chainbase modifier lambda
#     uint64_t             primary_key; //< primary_key should not be changed within a chainbase modifier lambda
#     account_name         payer;
#     vector<char>         value;
# };

class KeyValueObject(object):
    by_id = 0
    by_scope_primary = 1
    def __init__(self, table_id: I64, t_id: I64, primary_key: U64, payer: Name, value: bytes):
        self._table_id = table_id
        self.t_id = t_id
        self.primary_key = primary_key
        self.payer = payer
        self.value = value

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{t_id: {self.t_id}, primary_key: {self.primary_key}, payer: {self.payer}, value: {self.value}}}"

    def __eq__(self, other):
        return self.t_id == other.t_id \
            and self.primary_key == other.primary_key \
            and self.payer == other.payer \
            and self.value == other.value

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_i64(self.t_id)
        enc.pack_u64(self.primary_key)
        enc.pack_name(self.payer)
        enc.pack_bytes(self.value)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        t_id = dec.unpack_i64()
        primary_key = dec.unpack_u64()
        payer = dec.unpack_name()
        value = dec.unpack_bytes()
        return KeyValueObject(table_id, t_id, primary_key, payer, value)
    
    @classmethod
    def generate_key_by_scope_primary(cls, t_id: I64, primary_key: U64):
        return i2b(t_id) + u2b(primary_key)

# struct index64_object_ {
#     int64_t       t_id; //< t_id should not be changed within a chainbase modifier lambda
#     uint64_t      primary_key; //< primary_key should not be changed within a chainbase modifier lambda
#     account_name  payer;
#     uint64_t  secondary_key; //< secondary_key should not be changed within a chainbase modifier lambda
# };

class Index64Object(object):
    by_id = 0
    by_primary = 1
    by_secondary = 2

    def __init__(self, table_id: I64, t_id: I64, primary_key: U64, payer: Name, secondary_key: U64):
        self._table_id = table_id
        self.t_id = t_id
        self.primary_key = primary_key
        self.payer = payer
        self.secondary_key = secondary_key

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{t_id: {self.t_id}, primary_key: {self.primary_key}, payer: {self.payer}, secondary_key: {self.secondary_key}}}"

    def __eq__(self, other):
        return self.t_id == other.t_id \
            and self.primary_key == other.primary_key \
            and self.payer == other.payer \
            and self.secondary_key == other.secondary_key

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_i64(self.t_id)
        enc.pack_u64(self.primary_key)
        enc.pack_name(self.payer)
        enc.pack_u64(self.secondary_key)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        t_id = dec.unpack_i64()
        primary_key = dec.unpack_u64()
        payer = dec.unpack_name()
        secondary_key = dec.unpack_u64()
        return Index64Object(table_id, t_id, primary_key, payer, secondary_key)

    @classmethod
    def generate_key_by_primary(cls, t_id: I64, primary_key: U64):
        return i2b(t_id) + u2b(primary_key)
    
    @classmethod
    def generate_key_by_secondary(cls, t_id: I64, secondary_key: U64, primary_key: U64):
        return i2b(t_id) + u2b(secondary_key) + u2b(primary_key)

# struct index128_object_ {
#     int64_t       t_id; //< t_id should not be changed within a chainbase modifier lambda
#     uint64_t      primary_key; //< primary_key should not be changed within a chainbase modifier lambda
#     account_name  payer;
#     uint128_t  secondary_key; //< secondary_key should not be changed within a chainbase modifier lambda
# };

class Index128Object(object):
    by_id = 0
    by_primary = 1
    by_secondary = 2
    def __init__(self, table_id: I64, t_id: I64, primary_key: U64, payer: Name, secondary_key: U128):
        self._table_id = table_id
        self.t_id = t_id
        self.primary_key = primary_key
        self.payer = payer
        self.secondary_key = secondary_key

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{t_id: {self.t_id}, primary_key: {self.primary_key}, payer: {self.payer}, secondary_key: {self.secondary_key}}}"

    def __eq__(self, other):
        return self.t_id == other.t_id \
            and self.primary_key == other.primary_key \
            and self.payer == other.payer \
            and self.secondary_key == other.secondary_key

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_i64(self.t_id)
        enc.pack_u64(self.primary_key)
        enc.pack_name(self.payer)
        enc.pack_u128(self.secondary_key)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        t_id = dec.unpack_i64()
        primary_key = dec.unpack_u64()
        payer = dec.unpack_name()
        secondary_key = dec.unpack_u128()
        return Index128Object(table_id, t_id, primary_key, payer, secondary_key)

    @classmethod
    def generate_key_by_primary(cls, t_id: I64, primary_key: U64):
        return i2b(t_id) + u2b(primary_key)
    
    @classmethod
    def generate_key_by_secondary(cls, t_id: I64, secondary_key: U128, primary_key: U64):
        return i2b(t_id) + u2b(secondary_key, 16) + u2b(primary_key)


# struct index256_object_ {
#     int64_t       t_id; //< t_id should not be changed within a chainbase modifier lambda
#     uint64_t      primary_key; //< primary_key should not be changed within a chainbase modifier lambda
#     account_name  payer;
#     key256_t  secondary_key; //< secondary_key should not be changed within a chainbase modifier lambda
# };

class Index256Object(object):
    by_id = 0
    by_primary = 1
    by_secondary = 2
    def __init__(self, table_id: I64, t_id: I64, primary_key: U64, payer: Name, secondary_key: U256):
        self._table_id = table_id
        self.t_id = t_id
        self.primary_key = primary_key
        self.payer = payer
        self.secondary_key = secondary_key

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{t_id: {self.t_id}, primary_key: {self.primary_key}, payer: {self.payer}, secondary_key: {self.secondary_key}}}"

    def __eq__(self, other):
        return self.t_id == other.t_id \
            and self.primary_key == other.primary_key \
            and self.payer == other.payer \
            and self.secondary_key == other.secondary_key

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_i64(self.t_id)
        enc.pack_u64(self.primary_key)
        enc.pack_name(self.payer)
        enc.pack_u256(self.secondary_key)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        t_id = dec.unpack_i64()
        primary_key = dec.unpack_u64()
        payer = dec.unpack_name()
        secondary_key = dec.unpack_u256()
        return Index256Object(table_id, t_id, primary_key, payer, secondary_key)

    @classmethod
    def generate_key_by_primary(cls, t_id: I64, primary_key: U64):
        return i2b(t_id) + u2b(primary_key)
    
    @classmethod
    def generate_key_by_secondary(cls, t_id: I64, secondary_key: U256, primary_key: U64):
        return i2b(t_id) + u2b(secondary_key, 32) + u2b(primary_key)


# struct index_double_object_ {
#     int64_t       t_id; //< t_id should not be changed within a chainbase modifier lambda
#     uint64_t      primary_key; //< primary_key should not be changed within a chainbase modifier lambda
#     account_name  payer;
#     double  secondary_key; //< secondary_key should not be changed within a chainbase modifier lambda
# };

class IndexDoubleObject(object):
    by_id = 0
    by_primary = 1
    by_secondary = 2
    def __init__(self, table_id: I64, t_id: I64, primary_key: U64, payer: Name, secondary_key: float):
        self._table_id = table_id
        self.t_id = t_id
        self.primary_key = primary_key
        self.payer = payer
        self.secondary_key = secondary_key

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{t_id: {self.t_id}, primary_key: {self.primary_key}, payer: {self.payer}, secondary_key: {self.secondary_key}}}"

    def __eq__(self, other):
        return self.t_id == other.t_id \
            and self.primary_key == other.primary_key \
            and self.payer == other.payer \
            and self.secondary_key == other.secondary_key

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_i64(self.t_id)
        enc.pack_u64(self.primary_key)
        enc.pack_name(self.payer)
        enc.pack_double(self.secondary_key)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        t_id = dec.unpack_i64()
        primary_key = dec.unpack_u64()
        payer = dec.unpack_name()
        secondary_key = dec.unpack_double()
        return IndexDoubleObject(table_id, t_id, primary_key, payer, secondary_key)

    @classmethod
    def generate_key_by_primary(cls, t_id: I64, primary_key: U64):
        return i2b(t_id) + u2b(primary_key)
    
    @classmethod
    def generate_key_by_secondary(cls, t_id: I64, secondary_key: float, primary_key: U64):
        return i2b(t_id) + f2b(secondary_key) + u2b(primary_key)


# struct index_long_double_object_ {
#     int64_t       t_id; //< t_id should not be changed within a chainbase modifier lambda
#     uint64_t      primary_key; //< primary_key should not be changed within a chainbase modifier lambda
#     account_name  payer;
#     long double  secondary_key; //< secondary_key should not be changed within a chainbase modifier lambda
# };

class IndexLongDoubleObject(object):
    by_id = 0
    by_primary = 1
    by_secondary = 2
    def __init__(self, table_id: I64, t_id: I64, primary_key: U64, payer: Name, secondary_key: F128):
        self._table_id = table_id
        self.t_id = t_id
        self.primary_key = primary_key
        self.payer = payer
        self.secondary_key = secondary_key

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{t_id: {self.t_id}, primary_key: {self.primary_key}, payer: {self.payer}, secondary_key: {self.secondary_key}}}"

    def __eq__(self, other):
        return self.t_id == other.t_id \
            and self.primary_key == other.primary_key \
            and self.payer == other.payer \
            and self.secondary_key == other.secondary_key

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_i64(self.t_id)
        enc.pack_u64(self.primary_key)
        enc.pack_name(self.payer)
        enc.pack(self.secondary_key)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        t_id = dec.unpack_i64()
        primary_key = dec.unpack_u64()
        payer = dec.unpack_name()
        secondary_key = F128.unpack(dec)
        return IndexLongDoubleObject(table_id, t_id, primary_key, payer, secondary_key)

    @classmethod
    def generate_key_by_primary(cls, t_id: I64, primary_key: U64):
        return i2b(t_id) + u2b(primary_key)
    
    @classmethod
    def generate_key_by_secondary(cls, t_id: I64, secondary_key: F128, primary_key: U64):
        enc = Encoder()
        enc.pack_i64(t_id)
        enc.pack(secondary_key)
        enc.pack_u64(primary_key)
        return enc.get_bytes()

# struct block_signing_authority_v0 {
#    uint32_t                           threshold = 0;
#    vector<key_weight>   keys;
# };


class BlockSigningAuthorityV0(object):
    by_id = 0
    def __init__(self, threshold: U32, keys: List[KeyWeight]):
        self.threshold = threshold
        self.keys = keys

    def __repr__(self):
        return f"{{threshold: {self.threshold}, keys: {self.keys}}}"

    def __eq__(self, other):
        return self.threshold == other.threshold \
            and self.keys == other.keys

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_u32(self.threshold)
        enc.pack_list(self.keys)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        threshold = dec.unpack_u32()
        keys = dec.unpack_list(KeyWeight.unpack)
        return BlockSigningAuthorityV0(threshold, keys)

BlockSigningAuthority = Variant[BlockSigningAuthorityV0]

# struct producer_authority {
#    name                              producer_name;
#    block_signing_authority           authority;
# };

class ProducerAuthority(object):
    by_id = 0
    def __init__(self, producer_name: Name, authority: BlockSigningAuthority):
        self.producer_name = producer_name
        self.authority = authority

    def __repr__(self):
        return f"{{producer_name: {self.producer_name}, authority: {self.authority}}}"

    def __eq__(self, other):
        return self.producer_name == other.producer_name \
            and self.authority == other.authority

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_name(self.producer_name)
        enc.pack(self.authority)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        producer_name = dec.unpack_name()
        authority = BlockSigningAuthority.unpack(dec, BlockSigningAuthorityV0)
        return ProducerAuthority(producer_name, authority)

# struct producer_authority_schedule {
#    uint32_t                                       version = 0; ///< sequentially incrementing version number
#    vector<producer_authority>                     producers;
# }

class ProducerAuthoritySchedule(object):
    by_id = 0
    def __init__(self, version: U32, producers: List[ProducerAuthority]):
        self.version = version
        self.producers = producers

    def __repr__(self):
        return f"{{version: {self.version}, producers: {self.producers}}}"

    def __eq__(self, other):
        return self.version == other.version \
            and self.producers == other.producers

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_u32(self.version)
        enc.pack_list(self.producers)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        version = dec.unpack_u32()
        length = dec.unpack_length()
        producers = []
        for _ in range(length):
            producer = ProducerAuthority.unpack(dec)
            producers.append(producer)
        return ProducerAuthoritySchedule(version, producers)


# struct chain_config {
#    uint64_t   max_block_net_usage;                 ///< the maxiumum net usage in instructions for a block
#    uint32_t   target_block_net_usage_pct;          ///< the target percent (1% == 100, 100%= 10,000) of maximum net usage; exceeding this triggers congestion handling
#    uint32_t   max_transaction_net_usage;           ///< the maximum objectively measured net usage that the chain will allow regardless of account limits
#    uint32_t   base_per_transaction_net_usage;      ///< the base amount of net usage billed for a transaction to cover incidentals
#    uint32_t   net_usage_leeway;
#    uint32_t   context_free_discount_net_usage_num; ///< the numerator for the discount on net usage of context-free data
#    uint32_t   context_free_discount_net_usage_den; ///< the denominator for the discount on net usage of context-free data

#    uint32_t   max_block_cpu_usage;                 ///< the maxiumum billable cpu usage (in microseconds) for a block
#    uint32_t   target_block_cpu_usage_pct;          ///< the target percent (1% == 100, 100%= 10,000) of maximum cpu usage; exceeding this triggers congestion handling
#    uint32_t   max_transaction_cpu_usage;           ///< the maximum billable cpu usage (in microseconds) that the chain will allow regardless of account limits
#    uint32_t   min_transaction_cpu_usage;           ///< the minimum billable cpu usage (in microseconds) that the chain requires

#    uint32_t   max_transaction_lifetime;            ///< the maximum number of seconds that an input transaction's expiration can be ahead of the time of the block in which it is first included
#    uint32_t   deferred_trx_expiration_window;      ///< the number of seconds after the time a deferred transaction can first execute until it expires
#    uint32_t   max_transaction_delay;               ///< the maximum number of seconds that can be imposed as a delay requirement by authorization checks
#    uint32_t   max_inline_action_size;              ///< maximum allowed size (in bytes) of an inline action
#    uint16_t   max_inline_action_depth;             ///< recursion depth limit on sending inline actions
#    uint16_t   max_authority_depth;                 ///< recursion depth limit for checking if an authority is satisfied

#    uint32_t   max_action_return_value_size = config::default_max_action_return_value_size;               ///< size limit for action return value
# }   

class ChainConfig(object):
    def __init__(self,  max_block_net_usage: U64,
                        target_block_net_usage_pct: U32,
                        max_transaction_net_usage: U32,
                        base_per_transaction_net_usage: U32,
                        net_usage_leeway: U32,
                        context_free_discount_net_usage_num: U32,
                        context_free_discount_net_usage_den: U32,
                        max_block_cpu_usage: U32,
                        target_block_cpu_usage_pct: U32,
                        max_transaction_cpu_usage: U32,
                        min_transaction_cpu_usage: U32,
                        max_transaction_lifetime: U32,
                        deferred_trx_expiration_window: U32,
                        max_transaction_delay: U32,
                        max_inline_action_size: U32,
                        max_inline_action_depth: U16,
                        max_authority_depth: U16,
                        max_action_return_value_size: U32):
        self.max_block_net_usage = max_block_net_usage
        self.target_block_net_usage_pct = target_block_net_usage_pct
        self.max_transaction_net_usage = max_transaction_net_usage
        self.base_per_transaction_net_usage = base_per_transaction_net_usage
        self.net_usage_leeway = net_usage_leeway
        self.context_free_discount_net_usage_num = context_free_discount_net_usage_num
        self.context_free_discount_net_usage_den = context_free_discount_net_usage_den
        self.max_block_cpu_usage = max_block_cpu_usage
        self.target_block_cpu_usage_pct = target_block_cpu_usage_pct
        self.max_transaction_cpu_usage = max_transaction_cpu_usage
        self.min_transaction_cpu_usage = min_transaction_cpu_usage
        self.max_transaction_lifetime = max_transaction_lifetime
        self.deferred_trx_expiration_window = deferred_trx_expiration_window
        self.max_transaction_delay = max_transaction_delay
        self.max_inline_action_size = max_inline_action_size
        self.max_inline_action_depth = max_inline_action_depth
        self.max_authority_depth = max_authority_depth
        self.max_action_return_value_size = max_action_return_value_size
    def __repr__(self):
        return "ChainConfig(%s)" % (self.__dict__)

    def __str__(self):
        return "ChainConfig(%s)" % (self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack_u64(self.max_block_net_usage)
        enc.pack_u32(self.target_block_net_usage_pct)
        enc.pack_u32(self.max_transaction_net_usage)
        enc.pack_u32(self.base_per_transaction_net_usage)
        enc.pack_u32(self.net_usage_leeway)
        enc.pack_u32(self.context_free_discount_net_usage_num)
        enc.pack_u32(self.context_free_discount_net_usage_den)
        enc.pack_u32(self.max_block_cpu_usage)
        enc.pack_u32(self.target_block_cpu_usage_pct)
        enc.pack_u32(self.max_transaction_cpu_usage)
        enc.pack_u32(self.min_transaction_cpu_usage)
        enc.pack_u32(self.max_transaction_lifetime)
        enc.pack_u32(self.deferred_trx_expiration_window)
        enc.pack_u32(self.max_transaction_delay)
        enc.pack_u32(self.max_inline_action_size)
        enc.pack_u16(self.max_inline_action_depth)
        enc.pack_u16(self.max_authority_depth)
        enc.pack_u32(self.max_action_return_value_size)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        max_block_net_usage = dec.unpack_u64()
        target_block_net_usage_pct = dec.unpack_u32()
        max_transaction_net_usage = dec.unpack_u32()
        base_per_transaction_net_usage = dec.unpack_u32()
        net_usage_leeway = dec.unpack_u32()
        context_free_discount_net_usage_num = dec.unpack_u32()
        context_free_discount_net_usage_den = dec.unpack_u32()
        max_block_cpu_usage = dec.unpack_u32()
        target_block_cpu_usage_pct = dec.unpack_u32()
        max_transaction_cpu_usage = dec.unpack_u32()
        min_transaction_cpu_usage = dec.unpack_u32()
        max_transaction_lifetime = dec.unpack_u32()
        deferred_trx_expiration_window = dec.unpack_u32()
        max_transaction_delay = dec.unpack_u32()
        max_inline_action_size = dec.unpack_u32()
        max_inline_action_depth = dec.unpack_u16()
        max_authority_depth = dec.unpack_u16()
        max_action_return_value_size = dec.unpack_u32()
        return ChainConfig(max_block_net_usage,
                            target_block_net_usage_pct,
                            max_transaction_net_usage,
                            base_per_transaction_net_usage,
                            net_usage_leeway,
                            context_free_discount_net_usage_num,
                            context_free_discount_net_usage_den,
                            max_block_cpu_usage,
                            target_block_cpu_usage_pct,
                            max_transaction_cpu_usage,
                            min_transaction_cpu_usage,
                            max_transaction_lifetime,
                            deferred_trx_expiration_window,
                            max_transaction_delay,
                            max_inline_action_size,
                            max_inline_action_depth,
                            max_authority_depth,
                            max_action_return_value_size)

# struct kv_database_config {
#     std::uint32_t max_key_size   = 0; ///< the maximum size in bytes of a key
#     std::uint32_t max_value_size = 0; ///< the maximum size in bytes of a value
#     std::uint32_t max_iterators  = 0; ///< the maximum number of iterators that a contract can have simultaneously.
# };

class KvDatabaseConfig(object):
    def __init__(self, max_key_size: U32, max_value_size: U32, max_iterators: U32):
        self.max_key_size = max_key_size
        self.max_value_size = max_value_size
        self.max_iterators = max_iterators

    def __repr__(self):
        return "KvDatabaseConfig(%s)" % (self.__dict__)

    def __str__(self):
        return "KvDatabaseConfig(%s)" % (self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack_u32(self.max_key_size)
        enc.pack_u32(self.max_value_size)
        enc.pack_u32(self.max_iterators)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        max_key_size = dec.unpack_u32()
        max_value_size = dec.unpack_u32()
        max_iterators = dec.unpack_u32()
        return KvDatabaseConfig(max_key_size, max_value_size, max_iterators)

# struct wasm_config {
#    std::uint32_t max_mutable_global_bytes;
#    std::uint32_t max_table_elements;
#    std::uint32_t max_section_elements;
#    std::uint32_t max_linear_memory_init;
#    std::uint32_t max_func_local_bytes;
#    std::uint32_t max_nested_structures;
#    std::uint32_t max_symbol_bytes;
#    std::uint32_t max_module_bytes;
#    std::uint32_t max_code_bytes;
#    std::uint32_t max_pages;
#    std::uint32_t max_call_depth;
# };

class WasmConfig(object):
    def __init__(self, max_mutable_global_bytes: U32,
                max_table_elements: U32,
                max_section_elements: U32,
                max_linear_memory_init: U32,
                max_func_local_bytes: U32,
                max_nested_structures: U32,
                max_symbol_bytes: U32,
                max_module_bytes: U32,
                max_code_bytes: U32,
                max_pages: U32,
                max_call_depth: U32):
        self.max_mutable_global_bytes = max_mutable_global_bytes
        self.max_table_elements = max_table_elements
        self.max_section_elements = max_section_elements
        self.max_linear_memory_init = max_linear_memory_init
        self.max_func_local_bytes = max_func_local_bytes
        self.max_nested_structures = max_nested_structures
        self.max_symbol_bytes = max_symbol_bytes
        self.max_module_bytes = max_module_bytes
        self.max_code_bytes = max_code_bytes
        self.max_pages = max_pages
        self.max_call_depth = max_call_depth

    def __repr__(self):
        return "WasmConfig(%s)" % (self.__dict__)

    def __str__(self):
        return "WasmConfig(%s)" % (self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_u32(self.max_mutable_global_bytes)
        enc.pack_u32(self.max_table_elements)
        enc.pack_u32(self.max_section_elements)
        enc.pack_u32(self.max_linear_memory_init)
        enc.pack_u32(self.max_func_local_bytes)
        enc.pack_u32(self.max_nested_structures)
        enc.pack_u32(self.max_symbol_bytes)
        enc.pack_u32(self.max_module_bytes)
        enc.pack_u32(self.max_code_bytes)
        enc.pack_u32(self.max_pages)
        enc.pack_u32(self.max_call_depth)
        return enc.get_pos() - pos
    
    @classmethod
    def unpack(cls, dec: Decoder):
        max_mutable_global_bytes = dec.unpack_u32()
        max_table_elements = dec.unpack_u32()
        max_section_elements = dec.unpack_u32()
        max_linear_memory_init = dec.unpack_u32()
        max_func_local_bytes = dec.unpack_u32()
        max_nested_structures = dec.unpack_u32()
        max_symbol_bytes = dec.unpack_u32()
        max_module_bytes = dec.unpack_u32()
        max_code_bytes = dec.unpack_u32()
        max_pages = dec.unpack_u32()
        max_call_depth = dec.unpack_u32()
        return WasmConfig(max_mutable_global_bytes,
                        max_table_elements,
                        max_section_elements,
                        max_linear_memory_init,
                        max_func_local_bytes,
                        max_nested_structures,
                        max_symbol_bytes,
                        max_module_bytes,
                        max_code_bytes,
                        max_pages,
                        max_call_depth)

# struct global_property_object_ {
#     // id_type                             id;
#     std::optional<block_num_type>       proposed_schedule_block_num;
#     producer_authority_schedule         proposed_schedule;
#     chain_config                        configuration;
#     chain_id_type                       chain_id = chain_id_type::empty_chain_id();
#     kv_database_config                  kv_configuration;
#     wasm_config                         wasm_configuration;
# };

class GlobalPropertyObject(object):
    by_id = 0
    def __init__(self, table_id: I64,
                        proposed_schedule_block_num: Optional[U32],
                        proposed_schedule: ProducerAuthoritySchedule,
                        configuration: ChainConfig,
                        chain_id: Checksum256,
                        kv_configuration: KvDatabaseConfig, wasm_configuration: WasmConfig):
        self.proposed_schedule_block_num = proposed_schedule_block_num
        self.proposed_schedule = proposed_schedule
        self.configuration = configuration
        self.chain_id = chain_id
        self.kv_configuration = kv_configuration
        self.wasm_configuration = wasm_configuration

    def __repr__(self):
        return f"{{proposed_schedule_block_num: {self.proposed_schedule_block_num}, proposed_schedule: {self.proposed_schedule}, configuration: {self.configuration}, chain_id: {self.chain_id}, kv_configuration: {self.kv_configuration}, wasm_configuration: {self.wasm_configuration}}}"

    def __eq__(self, other):
        return self.proposed_schedule_block_num == other.proposed_schedule_block_num \
            and self.proposed_schedule == other.proposed_schedule \
            and self.configuration == other.configuration \
            and self.chain_id == other.chain_id \
            and self.kv_configuration == other.kv_configuration \
            and self.wasm_configuration == other.wasm_configuration

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_optional(self.proposed_schedule_block_num, U32)
        enc.pack(self.proposed_schedule)
        enc.pack(self.configuration)
        enc.pack(self.chain_id)
        enc.pack(self.kv_configuration)
        enc.pack(self.wasm_configuration)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        proposed_schedule_block_num = dec.unpack_optional(U32)
        proposed_schedule = ProducerAuthoritySchedule.unpack(dec)
        configuration = ChainConfig.unpack(dec)
        chain_id = dec.unpack_checksum256()
        kv_configuration = KvDatabaseConfig.unpack(dec)
        wasm_configuration = WasmConfig.unpack(dec)
        return GlobalPropertyObject(table_id, proposed_schedule_block_num, proposed_schedule, configuration, chain_id, kv_configuration, wasm_configuration)

# struct dynamic_global_property_object_ {
#     uint64_t   global_action_sequence = 0;
# };

class DynamicGlobalPropertyObject(object):
    by_id = 0
    def __init__(self, table_id: I64, global_action_sequence: U64):
        self._table_id = table_id
        self.global_action_sequence = global_action_sequence

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{global_action_sequence: {self.global_action_sequence}}}"

    def __eq__(self, other):
        return self.global_action_sequence == other.global_action_sequence

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_u64(self.global_action_sequence)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        global_action_sequence = dec.unpack_u64()
        return DynamicGlobalPropertyObject(table_id, global_action_sequence)


# struct block_summary_object_ {
#     block_id_type  block_id;
# };

class BlockSummaryObject(object):
    by_id = 0
    def __init__(self, table_id: I64, block_id: Checksum256):
        self._table_id = table_id
        self.block_id = block_id

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{block_id: {self.block_id}}}"

    def __eq__(self, other):
        return self.block_id == other.block_id

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack(self.block_id)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        block_id = dec.unpack(Checksum256)
        return BlockSummaryObject(table_id, block_id)

# struct transaction_object_ {
#     time_point_sec      expiration;
#     transaction_id_type trx_id; //< trx_id should not be changed within a chainbase modifier lambda
# };

class TransactionObject(object):
    by_id = 0
    by_trx_id = 1
    by_expiration = 2
    def __init__(self, table_id: I64, expiration: TimePointSec, trx_id: Checksum256):
        self._table_id = table_id
        self.expiration = expiration
        self.trx_id = trx_id

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{expiration: {self.expiration}, trx_id: {self.trx_id}}}"

    def __eq__(self, other):
        return self.expiration == other.expiration \
            and self.trx_id == other.trx_id

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_u32(self.expiration)
        enc.pack(self.trx_id)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        expiration = dec.unpack_u32()
        trx_id = dec.unpack(Checksum256)
        return TransactionObject(table_id, expiration, trx_id)
    
    @classmethod
    def generate_key_by_expiration(cls, expiration: U32, table_id: I64):
        return u2b(expiration, 4) + i2b(table_id)

# struct generated_transaction_object_ {
#     transaction_id_type           trx_id;
#     account_name                  sender;
#     uint128_t                     sender_id;
#     account_name                  payer;
#     time_point                    delay_until; /// this generated transaction will not be applied until the specified time
#     time_point                    expiration; /// this generated transaction will not be applied after this time
#     time_point                    published;
#     vector<char>                  packed_trx;
# };

class GeneratedTransactionObject(object):
    by_id = 0
    by_trx_id = 1
    by_expiration = 2
    by_delay = 3
    by_sender_id = 4

    def __init__(self, table_id: I64, trx_id: Checksum256, sender: Name, sender_id: U128, payer: Name, delay_until: TimePoint, expiration: TimePoint, published: TimePoint, packed_trx: bytes):
        self._table_id = table_id
        self.trx_id = trx_id
        self.sender = sender
        self.sender_id = sender_id
        self.payer = payer
        self.delay_until = delay_until
        self.expiration = expiration
        self.published = published
        self.packed_trx = packed_trx

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{trx_id: {self.trx_id}, sender: {self.sender}, sender_id: {self.sender_id}, payer: {self.payer}, delay_until: {self.delay_until}, expiration: {self.expiration}, published: {self.published}, packed_trx: {self.packed_trx}}}"

    def __eq__(self, other):
        return self.trx_id == other.trx_id \
            and self.sender == other.sender \
            and self.sender_id == other.sender_id \
            and self.payer == other.payer \
            and self.delay_until == other.delay_until \
            and self.expiration == other.expiration \
            and self.published == other.published \
            and self.packed_trx == other.packed_trx

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack(self.trx_id)
        enc.pack_name(self.sender)
        enc.pack_u128(self.sender_id)
        enc.pack_name(self.payer)
        enc.pack(self.delay_until)
        enc.pack(self.expiration)
        enc.pack(self.published)
        enc.pack_bytes(self.packed_trx)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        trx_id = dec.unpack_checksum256()
        sender = dec.unpack_name()
        sender_id = dec.unpack_u128()
        payer = dec.unpack_name()
        delay_until = TimePoint.unpack(dec)
        expiration = TimePoint.unpack(dec)
        published = TimePoint.unpack(dec)
        packed_trx = dec.unpack_bytes()
        return GeneratedTransactionObject(table_id,
                trx_id,
                sender,
                sender_id,
                payer,
                delay_until,
                expiration,
                published,
                packed_trx)

    @classmethod
    def generate_key_by_expiration(self, expiration: Union[I64, TimePoint], table_id: I64):
        if isinstance(expiration, TimePoint):
            expiration = expiration.time
        assert isinstance(expiration, int)
        return i2b(expiration) + i2b(table_id)

    @classmethod
    def generate_key_by_delay(self, delay_until: Union[I64, TimePoint], table_id: I64):
        if isinstance(delay_until, TimePoint):
            delay_until = delay_until.time
        assert isinstance(delay_until, int)
        return i2b(delay_until) + i2b(table_id)

    @classmethod
    def generate_key_by_sender_id(self, sender: Name, sender_id: U128):
        return  eos.s2b(sender) + u2b(sender_id, 16)

# struct table_id_object_ {
#     account_name   code;  //< code should not be changed within a chainbase modifier lambda
#     scope_name     scope; //< scope should not be changed within a chainbase modifier lambda
#     table_name     table; //< table should not be changed within a chainbase modifier lambda
#     account_name   payer;
#     uint32_t       count = 0; /// the number of elements in the table
# };

class TableIdObject(object):
    by_id = 0
    by_code_scope_table = 1
    def __init__(self, table_id: I64, code: Name, scope: Name, table: Name, payer: Name, count: U32):
        self._table_id = table_id
        self.code = code
        self.scope = scope
        self.table = table
        self.payer = payer
        self.count = count

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{code: {self.code}, scope: {self.scope}, table: {self.table}, payer: {self.payer}, count: {self.count}}}"

    def __eq__(self, other):
        return self.code == other.code \
            and self.scope == other.scope \
            and self.table == other.table \
            and self.payer == other.payer \
            and self.count == other.count

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_name(self.code)
        enc.pack_name(self.scope)
        enc.pack_name(self.table)
        enc.pack_name(self.payer)
        enc.pack_u32(self.count)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        code = dec.unpack_name()
        scope = dec.unpack_name()
        table = dec.unpack_name()
        payer = dec.unpack_name()
        count = dec.unpack_u32()
        return TableIdObject(table_id, code, scope, table, payer, count)

    @classmethod
    def generate_key_by_code_scope_table(cls, code: Name, scope: Name, table: Name):
        return eos.s2b(code) + eos.s2b(scope) + eos.s2b(table)

# struct resource_limits_object_ {
#     account_name owner; //< owner should not be changed within a chainbase modifier lambda
#     bool pending = false; //< pending should not be changed within a chainbase modifier lambda

#     int64_t net_weight = -1;
#     int64_t cpu_weight = -1;
#     int64_t ram_bytes = -1;
# };

class ResourceLimitsObject(object):
    by_id = 0
    by_owner = 1
    def __init__(self, table_id: I64, owner: Name, pending: bool, net_weight: I64, cpu_weight: I64, ram_bytes: I64):
        self._table_id = table_id
        self.owner = owner
        self.pending = pending
        self.net_weight = net_weight
        self.cpu_weight = cpu_weight
        self.ram_bytes = ram_bytes

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{owner: {self.owner}, pending: {self.pending}, net_weight: {self.net_weight}, cpu_weight: {self.cpu_weight}, ram_bytes: {self.ram_bytes}}}"

    def __eq__(self, other):
        return self.owner == other.owner \
            and self.net_weight == other.net_weight \
            and self.cpu_weight == other.cpu_weight \
            and self.ram_bytes == other.ram_bytes

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_name(self.owner)
        # enc.pack_bool(self.pending)
        enc.pack_i64(self.net_weight)
        enc.pack_i64(self.cpu_weight)
        enc.pack_i64(self.ram_bytes)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        owner = dec.unpack_name()
        pending = dec.unpack_bool()
        net_weight = dec.unpack_i64()
        cpu_weight = dec.unpack_i64()
        ram_bytes = dec.unpack_i64()
        return ResourceLimitsObject(table_id, owner, pending, net_weight, cpu_weight, ram_bytes)

    @classmethod
    def generate_key_by_owner(cls, pending: bool, owner: Name):
        if pending:
            return b'\x01' + eos.s2b(owner)
        else:
            return b'\x00' + eos.s2b(owner)

# struct usage_accumulator {
#          uint32_t   last_ordinal;  ///< The ordinal of the last period which has contributed to the average
#          uint64_t   value_ex;      ///< The current average pre-multiplied by Precision
#          uint64_t   consumed;       ///< The last periods average + the current periods contribution so far
# }

class UsageAccumulator(object):
    def __init__(self, last_ordinal: U32, value_ex: U64, consumed: U64):
        self.last_ordinal = last_ordinal
        self.value_ex = value_ex
        self.consumed = consumed

    def __repr__(self):
        return f"{{last_ordinal: {self.last_ordinal}, value_ex: {self.value_ex}, consumed: {self.consumed}}}"

    def __eq__(self, other):
        return self.last_ordinal == other.last_ordinal \
            and self.value_ex == other.value_ex \
            and self.consumed == other.consumed

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_u32(self.last_ordinal)
        enc.pack_u64(self.value_ex)
        enc.pack_u64(self.consumed)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        last_ordinal = dec.unpack_u32()
        value_ex = dec.unpack_u64()
        consumed = dec.unpack_u64()
        return UsageAccumulator(last_ordinal, value_ex, consumed)

# struct resource_usage_object_ {
#     account_name owner; //< owner should not be changed within a chainbase modifier lambda
#     usage_accumulator        net_usage;
#     usage_accumulator        cpu_usage;
#     uint64_t                 ram_usage = 0;
# };

class ResourceUsageObject(object):
    by_id = 0
    by_owner = 1
    def __init__(self, table_id: I64, owner: Name, net_usage: UsageAccumulator, cpu_usage: UsageAccumulator, ram_usage: U64):
        self._table_id = table_id
        self.owner = owner
        self.net_usage = net_usage
        self.cpu_usage = cpu_usage
        self.ram_usage = ram_usage

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{owner: {self.owner}, net_usage: {self.net_usage}, cpu_usage: {self.cpu_usage}, ram_usage: {self.ram_usage}}}"

    def __eq__(self, other):
        return self.owner == other.owner \
            and self.net_usage == other.net_usage \
            and self.cpu_usage == other.cpu_usage \
            and self.ram_usage == other.ram_usage

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_name(self.owner)
        enc.pack(self.net_usage)
        enc.pack(self.cpu_usage)
        enc.pack_u64(self.ram_usage)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        owner = dec.unpack_name()
        net_usage = UsageAccumulator.unpack(dec)
        cpu_usage = UsageAccumulator.unpack(dec)
        ram_usage = dec.unpack_u64()
        return ResourceUsageObject(table_id, owner, net_usage, cpu_usage, ram_usage)

# struct resource_limits_state_object_ {
#     resource_limits::usage_accumulator average_block_net_usage;
#     resource_limits::usage_accumulator average_block_cpu_usage;

#     // void update_virtual_net_limit( const resource_limits_config_object& cfg );
#     // void update_virtual_cpu_limit( const resource_limits_config_object& cfg );

#     uint64_t pending_net_usage = 0ULL;
#     uint64_t pending_cpu_usage = 0ULL;

#     uint64_t total_net_weight = 0ULL;
#     uint64_t total_cpu_weight = 0ULL;
#     uint64_t total_ram_bytes = 0ULL;

#     uint64_t virtual_net_limit = 0ULL;
#     uint64_t virtual_cpu_limit = 0ULL;

# };

class ResourceLimitsStateObject(object):
    by_id = 0
    def __init__(self, table_id: I64,
                average_block_net_usage: UsageAccumulator,
                average_block_cpu_usage: UsageAccumulator,
                pending_net_usage: U64,
                pending_cpu_usage: U64,
                total_net_weight: U64,
                total_cpu_weight: U64,
                total_ram_bytes: U64,
                virtual_net_limit: U64,
                virtual_cpu_limit: U64):
        self._table_id = table_id
        self.average_block_net_usage = average_block_net_usage
        self.average_block_cpu_usage = average_block_cpu_usage
        self.pending_net_usage = pending_net_usage
        self.pending_cpu_usage = pending_cpu_usage
        self.total_net_weight = total_net_weight
        self.total_cpu_weight = total_cpu_weight
        self.total_ram_bytes = total_ram_bytes
        self.virtual_net_limit = virtual_net_limit
        self.virtual_cpu_limit = virtual_cpu_limit

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{average_block_net_usage: {self.average_block_net_usage}, average_block_cpu_usage: {self.average_block_cpu_usage}, pending_net_usage: {self.pending_net_usage}, pending_cpu_usage: {self.pending_cpu_usage}, total_net_weight: {self.total_net_weight}, total_cpu_weight: {self.total_cpu_weight}, total_ram_bytes: {self.total_ram_bytes}, virtual_net_limit: {self.virtual_net_limit}, virtual_cpu_limit: {self.virtual_cpu_limit}}}"
    
    def __eq__(self, other):
        return self.average_block_net_usage == other.average_block_net_usage \
            and self.average_block_cpu_usage == other.average_block_cpu_usage \
            and self.pending_net_usage == other.pending_net_usage \
            and self.pending_cpu_usage == other.pending_cpu_usage \
            and self.total_net_weight == other.total_net_weight \
            and self.total_cpu_weight == other.total_cpu_weight \
            and self.total_ram_bytes == other.total_ram_bytes \
            and self.virtual_net_limit == other.virtual_net_limit \
            and self.virtual_cpu_limit == other.virtual_cpu_limit
    
    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack(self.average_block_net_usage)
        enc.pack(self.average_block_cpu_usage)
        enc.pack_u64(self.pending_net_usage)
        enc.pack_u64(self.pending_cpu_usage)
        enc.pack_u64(self.total_net_weight)
        enc.pack_u64(self.total_cpu_weight)
        enc.pack_u64(self.total_ram_bytes)
        enc.pack_u64(self.virtual_net_limit)
        enc.pack_u64(self.virtual_cpu_limit)
        return enc.get_pos() - pos
    
    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        average_block_net_usage = UsageAccumulator.unpack(dec)
        average_block_cpu_usage = UsageAccumulator.unpack(dec)
        pending_net_usage = dec.unpack_u64()
        pending_cpu_usage = dec.unpack_u64()
        total_net_weight = dec.unpack_u64()
        total_cpu_weight = dec.unpack_u64()
        total_ram_bytes = dec.unpack_u64()
        virtual_net_limit = dec.unpack_u64()
        virtual_cpu_limit = dec.unpack_u64()
        return ResourceLimitsStateObject(table_id, average_block_net_usage, average_block_cpu_usage, pending_net_usage, pending_cpu_usage, total_net_weight, total_cpu_weight, total_ram_bytes, virtual_net_limit, virtual_cpu_limit)

# struct ratio {
#     uint64_t numerator;
#     uint64_t denominator;
# };

class Ratio(object):
    def __init__(self, numerator: U64, denominator: U64):
        self.numerator = numerator
        self.denominator = denominator

    def __repr__(self):
        return f"{{numerator: {self.numerator}, denominator: {self.denominator}}}"
    
    def __eq__(self, other):
        return self.numerator == other.numerator and self.denominator == other.denominator
    
    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_u64(self.numerator)
        enc.pack_u64(self.denominator)
        return enc.get_pos() - pos
    
    @classmethod
    def unpack(cls, dec: Decoder):
        numerator = dec.unpack_u64()
        denominator = dec.unpack_u64()
        return Ratio(numerator, denominator)

# struct elastic_limit_parameters {
#     uint64_t target;           // the desired usage
#     uint64_t max;              // the maximum usage
#     uint32_t periods;          // the number of aggregation periods that contribute to the average usage

#     uint32_t max_multiplier;   // the multiplier by which virtual space can oversell usage when uncongested
#     ratio    contract_rate;    // the rate at which a congested resource contracts its limit
#     ratio    expand_rate;       // the rate at which an uncongested resource expands its limits
# }

class ElasticLimitParameters(object):
    def __init__(self, target: U64, max: U64, periods: U32, max_multiplier: U32, contract_rate: Ratio, expand_rate: Ratio):
        self.target = target
        self.max = max
        self.periods = periods
        self.max_multiplier = max_multiplier
        self.contract_rate = contract_rate
        self.expand_rate = expand_rate
    
    def __repr__(self):
        return f"{{target: {self.target}, max: {self.max}, periods: {self.periods}, max_multiplier: {self.max_multiplier}, contract_rate: {self.contract_rate}, expand_rate: {self.expand_rate}}}"
    
    def __eq__(self, other):
        return self.target == other.target \
            and self.max == other.max \
            and self.periods == other.periods \
            and self.max_multiplier == other.max_multiplier \
            and self.contract_rate == other.contract_rate \
            and self.expand_rate == other.expand_rate
    
    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_u64(self.target)
        enc.pack_u64(self.max)
        enc.pack_u32(self.periods)
        enc.pack_u32(self.max_multiplier)
        enc.pack(self.contract_rate)
        enc.pack(self.expand_rate)
        return enc.get_pos() - pos
    
    @classmethod
    def unpack(cls, dec: Decoder):
        target = dec.unpack_u64()
        max = dec.unpack_u64()
        periods = dec.unpack_u32()
        max_multiplier = dec.unpack_u32()
        contract_rate = Ratio.unpack(dec)
        expand_rate = Ratio.unpack(dec)
        return ElasticLimitParameters(target, max, periods, max_multiplier, contract_rate, expand_rate)

# struct resource_limits_config_object_ {

#     resource_limits::elastic_limit_parameters cpu_limit_parameters = {EOS_PERCENT(config::default_max_block_cpu_usage, config::default_target_block_cpu_usage_pct), config::default_max_block_cpu_usage, config::block_cpu_usage_average_window_ms / config::block_interval_ms, 1000, {99, 100}, {1000, 999}};
#     resource_limits::elastic_limit_parameters net_limit_parameters = {EOS_PERCENT(config::default_max_block_net_usage, config::default_target_block_net_usage_pct), config::default_max_block_net_usage, config::block_size_average_window_ms / config::block_interval_ms, 1000, {99, 100}, {1000, 999}};

#     uint32_t account_cpu_usage_average_window = config::account_cpu_usage_average_window_ms / config::block_interval_ms;
#     uint32_t account_net_usage_average_window = config::account_net_usage_average_window_ms / config::block_interval_ms;
# };

class ResourceLimitsConfigObject(object):
    by_id = 0
    def __init__(self, table_id: I64, cpu_limit_parameters: ElasticLimitParameters, net_limit_parameters: ElasticLimitParameters, account_cpu_usage_average_window: U32, account_net_usage_average_window: U32):
        self._table_id = table_id
        self.cpu_limit_parameters = cpu_limit_parameters
        self.net_limit_parameters = net_limit_parameters
        self.account_cpu_usage_average_window = account_cpu_usage_average_window
        self.account_net_usage_average_window = account_net_usage_average_window
    
    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{cpu_limit_parameters: {self.cpu_limit_parameters}, net_limit_parameters: {self.net_limit_parameters}, account_cpu_usage_average_window: {self.account_cpu_usage_average_window}, account_net_usage_average_window: {self.account_net_usage_average_window}}}"
    
    def __eq__(self, other):
        return self.cpu_limit_parameters == other.cpu_limit_parameters \
            and self.net_limit_parameters == other.net_limit_parameters \
            and self.account_cpu_usage_average_window == other.account_cpu_usage_average_window \
            and self.account_net_usage_average_window == other.account_net_usage_average_window
    
    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack(self.cpu_limit_parameters)
        enc.pack(self.net_limit_parameters)
        enc.pack_u32(self.account_cpu_usage_average_window)
        enc.pack_u32(self.account_net_usage_average_window)
        return enc.get_pos() - pos
    
    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        cpu_limit_parameters = ElasticLimitParameters.unpack(dec)
        net_limit_parameters = ElasticLimitParameters.unpack(dec)
        account_cpu_usage_average_window = dec.unpack_u32()
        account_net_usage_average_window = dec.unpack_u32()
        return ResourceLimitsConfigObject(table_id, cpu_limit_parameters, net_limit_parameters, account_cpu_usage_average_window, account_net_usage_average_window)

# struct activated_protocol_feature_ {
#     digest_type feature_digest;
#     uint32_t    activation_block_num = 0;
# };

class ActivatedProtocolFeature(object):
    def __init__(self, feature_digest: Checksum256, activation_block_num: U32):
        self.feature_digest = feature_digest
        self.activation_block_num = activation_block_num
    
    def __repr__(self):
        return f"{{feature_digest: {self.feature_digest}, activation_block_num: {self.activation_block_num}}}"
    
    def __eq__(self, other):
        return self.feature_digest == other.feature_digest and self.activation_block_num == other.activation_block_num
    
    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack(self.feature_digest)
        enc.pack_u32(self.activation_block_num)
        return enc.get_pos() - pos
    
    @classmethod
    def unpack(cls, dec: Decoder):
        feature_digest = Checksum256.unpack(dec)
        activation_block_num = dec.unpack_u32()
        return ActivatedProtocolFeature(feature_digest, activation_block_num)

# struct protocol_state_object_ {
#     vector<activated_protocol_feature_>        activated_protocol_features;
#     vector<digest_type>                        preactivated_protocol_features;
#     vector<string>                             whitelisted_intrinsics;
#     uint32_t                                   num_supported_key_types = 0;
# };

class ProtocolStateObject(object):
    by_id = 0
    def __init__(self, table_id: I64, activated_protocol_features: List[ActivatedProtocolFeature], preactivated_protocol_features: List[Checksum256], whitelisted_intrinsics: List[str], num_supported_key_types: U32):
        self._table_id = table_id
        self.activated_protocol_features = activated_protocol_features
        self.preactivated_protocol_features = preactivated_protocol_features
        self.whitelisted_intrinsics = whitelisted_intrinsics
        self.num_supported_key_types = num_supported_key_types
    
    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{activated_protocol_features: {self.activated_protocol_features}, preactivated_protocol_features: {self.preactivated_protocol_features}, whitelisted_intrinsics: {self.whitelisted_intrinsics}, num_supported_key_types: {self.num_supported_key_types}}}"
    
    def __eq__(self, other):
        return self.activated_protocol_features == other.activated_protocol_features \
            and self.preactivated_protocol_features == other.preactivated_protocol_features \
            and self.whitelisted_intrinsics == other.whitelisted_intrinsics \
            and self.num_supported_key_types == other.num_supported_key_types
    
    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_list(self.activated_protocol_features)
        enc.pack_list(self.preactivated_protocol_features)
        enc.pack_list(self.whitelisted_intrinsics)
        enc.pack_u32(self.num_supported_key_types)
        return enc.get_pos() - pos
    
    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        activated_protocol_features = dec.unpack_list(ActivatedProtocolFeature)
        preactivated_protocol_features = dec.unpack_list(Checksum256)
        whitelisted_intrinsics = []
        length = dec.unpack_length()
        for i in range(length):
            _ = dec.unpack_u64()
            s = dec.unpack_string()
            whitelisted_intrinsics.append(s)
        num_supported_key_types = dec.unpack_u32()
        return ProtocolStateObject(table_id, activated_protocol_features, preactivated_protocol_features, whitelisted_intrinsics, num_supported_key_types)

# struct account_ram_correction_object_ {
#     account_name name; //< name should not be changed within a chainbase modifier lambda
#     uint64_t     ram_correction = 0;
# };

class AccountRamCorrectionObject(object):
    by_id = 0
    def __init__(self, table_id: I64, name: Name, ram_correction: U64):
        self._table_id = table_id
        self.name = name
        self.ram_correction = ram_correction

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{name: {self.name}, ram_correction: {self.ram_correction}}}"
    
    def __eq__(self, other):
        return self.name == other.name and self.ram_correction == other.ram_correction
    
    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_name(self.name)
        enc.pack_u64(self.ram_correction)
        return enc.get_pos() - pos
    
    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        name = dec.unpack_name()
        ram_correction = dec.unpack_u64()
        return AccountRamCorrectionObject(table_id, name, ram_correction)


# struct code_object_ {
#     digest_type  code_hash; //< code_hash should not be changed within a chainbase modifier lambda
#     vector<char>  code;
#     uint64_t     code_ref_count;
#     uint32_t     first_block_used;
#     uint8_t      vm_type = 0; //< vm_type should not be changed within a chainbase modifier lambda
#     uint8_t      vm_version = 0; //< vm_version should not be changed within a chainbase modifier lambda
# };

class CodeObject(object):
    by_id = 0
    by_code_hash = 1
    def __init__(self, table_id: I64, code_hash: Checksum256, code: List[str], code_ref_count: U64, first_block_used: U32, vm_type: U8, vm_version: U8):
        self._table_id = table_id
        self.code_hash = code_hash
        self.code = code
        self.code_ref_count = code_ref_count
        self.first_block_used = first_block_used
        self.vm_type = vm_type
        self.vm_version = vm_version

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{code_hash: {self.code_hash}, code: {self.code}, code_ref_count: {self.code_ref_count}, first_block_used: {self.first_block_used}, vm_type: {self.vm_type}, vm_version: {self.vm_version}}}"
    
    def __eq__(self, other):
        return self.code_hash == other.code_hash \
            and self.code == other.code \
            and self.code_ref_count == other.code_ref_count \
            and self.first_block_used == other.first_block_used \
            and self.vm_type == other.vm_type \
            and self.vm_version == other.vm_version
    
    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack(self.code_hash)
        enc.pack_bytes(self.code)
        enc.pack_u64(self.code_ref_count)
        enc.pack_u32(self.first_block_used)
        enc.pack_u8(self.vm_type)
        enc.pack_u8(self.vm_version)
        return enc.get_pos() - pos
    
    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        code_hash = Checksum256.unpack(dec)
        code = dec.unpack_bytes()
        code_ref_count = dec.unpack_u64()
        first_block_used = dec.unpack_u32()
        vm_type = dec.unpack_u8()
        vm_version = dec.unpack_u8()
        return CodeObject(table_id, code_hash, code, code_ref_count, first_block_used, vm_type, vm_version)

# struct database_header_object_ {
#     uint32_t       version;
# };

class DatabaseHeaderObject(object):
    by_id = 0
    def __init__(self, table_id: I64, version: U32):
        self._table_id = table_id
        self.version = version

    @property
    def table_id(self):
        return self._table_id

    def __repr__(self):
        return f"{{version: {self.version}}}"
    
    def __eq__(self, other):
        return self.version == other.version
    
    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_u32(self.version)
        return enc.get_pos() - pos
    
    @classmethod
    def unpack(cls, dec: Decoder):
        table_id = dec.unpack_i64()
        version = dec.unpack_u32()
        return DatabaseHeaderObject(table_id, version)
