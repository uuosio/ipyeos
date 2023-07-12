from typing import Generic, List, Type, TypeVar

from .packer import Decoder, Encoder, Packer
from .types import I64, U8, U16, U32, U64, Name, PublicKey

T = TypeVar('T')

class KeyWeight(Packer):
    #           shared_public_key key;
    #           weight_type       weight;
    def __init__(self, key: PublicKey, weight: U16):
        self.key = key
        self.weight = weight

    def __repr__(self):
        return f"{{key: {self.key}, weight: {self.weight}}}"

    def __eq__(self, other) -> bool:
        return self.key == other.key and self.weight == other.weight

    def pack(self, enc: Encoder):
        enc.pack(self.key)
        enc.pack_u16(self.weight)
        return 34 + 2

    @classmethod
    def unpack(self, dec: Decoder):
        key = dec.unpack_public_key()
        weight = dec.unpack_u16()
        return KeyWeight(key, weight)

class PermissionLevel(Packer):

    def __init__(self, actor: Name, permission: Name):
        self.actor = actor
        self.permission = permission

    def __repr__(self):
        return f"{{actor: {self.actor}, permission: {self.permission})}}"

    def __eq__(self, other) -> bool:
        return self.actor == other.actor and self.permission == other.permission

    def pack(self):
        return eos.s2b(self.actor) + eos.s2b(self.permission)

    @classmethod
    def unpack(self, dec: Decoder):
        actor = dec.unpack_name()
        permission = dec.unpack_name()
        return PermissionLevel(actor, permission)

class PermissionLevelWeight(Packer):
    #       shared_vector<permission_level_weight>     accounts;
    #           permission_level  permission;
    #           weight_type       weight;
    def __init__(self, permission: PermissionLevel, weight: U16):
        self.permission = permission
        self.weight = weight

    def __repr__(self):
        return f"{{permission: {self.permission}, weight: {self.weight}}}"

    def __eq__(self, other) -> bool:
        return self.permission == other.permission and self.weight == other.weight

    def pack(self):
        return self.permission.pack() + int.to_bytes(self.weight, 2, 'little')

    @classmethod
    def unpack(cls, dec: Decoder):
        permission = PermissionLevel.unpack(dec)
        weight = dec.unpack_u16()
        return PermissionLevelWeight(permission, weight)

class WaitWeight(Packer):
    #           uint32_t     wait_sec;
    #           weight_type  weight;
    def __init__(self, wait_sec: U32, weight: U16):
        self.wait_sec = wait_sec
        self.weight = weight

    def __repr__(self):
        return f"{{wait_sec: self.wait_sec, weight: self.weight}}"

    def __eq__(self, other) -> bool:
        return self.wait_sec == other.wait_sec and self.weight == other.weight

    def pack(self, enc: Encoder):
        enc.pack_u32(self.wait_sec)
        enc.pack_u16(self.weight)
        return 4 + 2

    @classmethod
    def unpack(cls, dec):
        wait_sec = dec.unpack_u32()
        weight = dec.unpack_u16()
        return WaitWeight(wait_sec, weight)

class Authority(Packer):
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

    def __init__(self, threshold: U32, keys: List[KeyWeight], accounts: List[PermissionLevelWeight], waits: List[WaitWeight]):
        self.threshold = threshold
        self.keys = keys
        self.accounts = accounts
        self.waits = waits

    def __repr__(self):
        return f"{{threshold: {self.threshold}, keys: {self.keys}, accounts: {self.accounts}, waits: {self.waits}}}"

    def __eq__(self, other) -> bool:
        return self.threshold == other.threshold and self.keys == other.keys \
                and self.accounts == other.accounts and self.waits == other.waits

    def pack(self, enc: Encoder):
        enc.pack_u32(self.threshold)
        enc.pack_length(len(self.keys))
        for key in self.keys:
            key.pack(enc)

        enc.pack_length(len(self.accounts))
        for a in self.accounts:
            a.pack(enc)

        enc.pack_length(len(self.waits))
        for wait in self.waits:
            wait.pack(enc)

    @classmethod
    def unpack(cls, dec: Decoder):
        threshold = dec.unpack_u32()

        length = dec.unpack_length()
        keys: List[KeyWeight] = []
        for i in range(length):
            keys.append(KeyWeight.unpack(dec))

        length = dec.unpack_length()
        accounts: List[PermissionLevelWeight] = []
        for i in range(length):
            accounts.append(PermissionLevelWeight.unpack(dec))

        length = dec.unpack_length()
        waits: List[WaitWeight] = []
        for i in range(length):
            waits.append(WaitWeight.unpack(dec))

        return Authority(threshold, keys, accounts, waits)

class Variant(Generic[T]):
    def __init__(self, type_id: U8, value: T):
        self.type_id = type_id
        self.value = value

    def __repr__(self):
        return f"{{type_id: {self.type_id}, value: {self.value}}}"
    
    def __eq__(self, other) -> bool:
        return self.type_id == other.type_id and self.value == other.value
    
    def pack(self, enc: Encoder):
        enc.pack_u8(self.type_id)
        self.value.pack(enc)
    
    @classmethod
    def unpack(cls, dec: Decoder, tp: T):
        type_id = dec.unpack_u8()
        value = tp.unpack(dec)
        return Variant(type_id, value)


class TimePoint(Packer):
    def __init__(self, time: I64):
        self.time = time

    def __repr__(self):
        return f"{{time: {self.time}}}"

    def __eq__(self, other) -> bool:
        return self.time == other.time

    def pack(self, enc: Encoder):
        enc.pack_i64(self.time)

    @classmethod
    def unpack(cls, dec: Decoder):
        time = dec.unpack_i64()
        return TimePoint(time)

# class TimePointSec(object):
#     def __init__(self, utc_seconds: U32):
#         self.utc_seconds = utc_seconds

#     def __repr__(self):
#         return f"{{utc_seconds: {self.utc_seconds}}}"

#     def __eq__(self, other) -> bool:
#         return self.utc_seconds == other.utc_seconds

#     def pack(self, enc: Encoder):
#         enc.pack_u32(self.utc_seconds)

#     @classmethod
#     def unpack(cls, dec: Decoder):
#         utc_seconds = dec.unpack_u32()
#         return TimePointSec(utc_seconds)

class Symbol(Packer):
    def __init__(self, precision: U8, name: str):
        assert len(name) <= 7 and name.isupper()
        assert precision <= 18
        self.precision = precision
        self.name = name

    def __repr__(self):
        return f"{{precision: {self.precision}, name: {self.name}}}"

    def __eq__(self, other) -> bool:
        return self.precision == other.precision and self.name == other.name
    
    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack_u8(self.precision)
        name = self.name.encode()
        enc.write_bytes(name + b'\x00' * (7 - len(name)))
        return enc.get_pos() - pos

    @classmethod
    def unpack(self, dec: Decoder):
        precision = dec.unpack_u8()
        name = dec.read_bytes(7)
        name = name.rstrip(b'\x00').decode()
        return Symbol(precision, name)

class Asset(Packer):
    def __init__(self, amount: I64, symbol: Symbol):
        self.amount = amount
        self.symbol = symbol

    def __repr__(self):
        return f"{{amount: {self.amount}, symbol: {self.symbol}}}"

    def __eq__(self, other) -> bool:
        return self.amount == other.amount and self.symbol == other.symbol

    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_i64(self.amount)
        enc.pack(self.symbol)
        return enc.get_pos() - pos

    def unpack(dec: Decoder):
        amount = dec.unpack_i64()
        symbol = Symbol.unpack(dec)
        return Asset(amount, symbol)

class Transfer(Packer):
    def __init__(self, sender: Name, recipient: Name, quantity: Asset, memo: str):
        self.sender = sender
        self.recipient = recipient
        self.quantity = quantity
        self.memo = memo

    def __repr__(self):
        return f"{{sender: {self.sender}, recipient: {self.recipient}, quantity: {self.quantity}, memo: {self.memo}}}"
    
    def __eq__(self, other) -> bool:
        return self.sender == other.sender and self.recipient == other.recipient \
                and self.quantity == other.quantity and self.memo == other.memo
    
    def pack(self, enc: Encoder) -> int:
        pos = enc.get_pos()
        enc.pack_name(self.sender)
        enc.pack_name(self.recipient)
        enc.pack(self.quantity)
        enc.pack_string(self.memo)
        return enc.get_pos() - pos
    
    @classmethod
    def unpack(cls, dec: Decoder):
        sender = dec.unpack_name()
        recipient = dec.unpack_name()
        quantity = Asset.unpack(dec)
        memo = dec.unpack_string()
        return cls(sender, recipient, quantity, memo)
