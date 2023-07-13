import hashlib
import time
from typing import List, Optional

from .packer import Decoder, Encoder, Packer
from .types import U16, U32, U64, Checksum256, Name, PublicKey

# struct producer_key {
#     account_name      producer_name;
#     public_key_type   block_signing_key;
# };

block_timestamp_epoch = 946684800000
block_interval_ms = 500

class ProducerKey(object):
    def __init__(self, producer_name: Name, block_signing_key: PublicKey):
        self.producer_name = producer_name
        self.block_signing_key = block_signing_key

    def pack(self, enc: Encoder):
        enc.pack_name(self.producer_name)
        enc.pack(self.block_signing_key)
        return 8 + 34

    @classmethod
    def unpack(cls, dec: Decoder):
        producer_name = dec.unpack_name()
        block_signing_key = dec.unpack_public_key()
        return cls(producer_name, block_signing_key)

# struct producer_schedule_type {
#     uint32_t                                       version = 0; ///< sequentially incrementing version number
#     vector<producer_key>                           producers;
# };

class ProducerSchedule(object):
    def __init__(self, version: U32, producers: List[ProducerKey]):
        self.version = version
        self.producers = producers

    def pack(self, enc: Encoder):
        pos = enc.pos
        enc.pack_u32(self.version)
        enc.pack_array(self.producers)
        return enc.pos - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        version = dec.unpack_u32()
        producers = dec.unpack_list(ProducerKey)
        return cls(version, producers)

# struct block_header
# {
#     block_timestamp_type             timestamp;
#     account_name                     producer;

#     /**
#     *  By signing this block this producer is confirming blocks [block_num() - confirmed, blocknum())
#     *  as being the best blocks for that range and that he has not signed any other
#     *  statements that would contradict.
#     *
#     *  No producer should sign a block with overlapping ranges or it is proof of byzantine
#     *  behavior. When producing a block a producer is always confirming at least the block he
#     *  is building off of.  A producer cannot confirm "this" block, only prior blocks.
#     */
#     uint16_t                         confirmed = 1;

#     block_id_type                    previous;

#     checksum256_type                 transaction_mroot; /// mroot of cycles_summary
#     checksum256_type                 action_mroot; /// mroot of all delivered action receipts

#     /**
#     * LEGACY SUPPORT - After enabling the wtmsig-blocks extension this field is deprecated and must be empty
#     *
#     * Prior to that activation this carries:
#     *
#     * The producer schedule version that should validate this block, this is used to
#     * indicate that the prior block which included new_producers->version has been marked
#     * irreversible and that it the new producer schedule takes effect this block.
#     */

#     using new_producers_type = std::optional<legacy::producer_schedule_type>;

#     uint32_t                          schedule_version = 0;
#     new_producers_type                new_producers;
#     extensions_type                   header_extensions;


#     block_header() = default;

#     digest_type       digest()const;
#     block_id_type     calculate_id() const;
#     uint32_t          block_num() const { return num_from_id(previous) + 1; }
#     static uint32_t   num_from_id(const block_id_type& id);

#     flat_multimap<uint16_t, block_header_extension> validate_and_extract_header_extensions()const;
# };

# using extensions_type = std::vector<std::pair<uint16_t, bytes>>;


class Pair(object):
    def __init__(self, first: U16, second: bytes):
        self.first = first
        self.second = second

    def pack(self, enc: Encoder):
        enc.pack_u16(self.first)
        enc.pack_bytes(self.second)
    
    @classmethod
    def unpack(cls, dec: Decoder):
        first = dec.unpack_u16()
        second = dec.unpack_bytes()
        return cls(first, second)

class BlockHeader(Packer):
    def __init__(self, timestamp: U32,
                    producer: Name,
                    confirmed: U16,
                    previous: Checksum256,
                    transaction_mroot: Checksum256,
                    action_mroot: Checksum256,
                    schedule_version: U32,
                    new_producers: Optional[ProducerSchedule],
                    header_extensions: List[Pair]):
        self.timestamp = timestamp
        self.producer = producer
        self.confirmed = confirmed
        self.previous = previous
        self.transaction_mroot = transaction_mroot
        self.action_mroot = action_mroot
        self.schedule_version = schedule_version
        self.new_producers = new_producers
        self.header_extensions = header_extensions
    
    def block_num(self):
        return int.from_bytes(self.previous.to_bytes()[:4], 'big') + 1

    def block_time_ms(self) -> str:
        msec = self.timestamp * block_interval_ms
        msec += block_timestamp_epoch
        return msec

    def block_time(self) -> str:
        msec = self.timestamp * block_interval_ms
        msec += block_timestamp_epoch
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msec / 1000))

    def __repr__(self):
        return f'BlockHeader(timestamp: {self.timestamp}, producer: {self.producer}, confirmed: {self.confirmed}, previous: {self.previous}, transaction_mroot: {self.transaction_mroot}, action_mroot: {self.action_mroot}, schedule_version: {self.schedule_version}, new_producers: {self.new_producers}, header_extensions: {self.header_extensions})'

    def __str__(self):
        return self.__repr__()

    def pack(self, enc: Encoder):
        enc.pack_u32(self.timestamp)
        enc.pack_name(self.producer)
        enc.pack_u16(self.confirmed)
        enc.pack(self.previous)
        enc.pack(self.transaction_mroot)
        enc.pack(self.action_mroot)
        enc.pack_u32(self.schedule_version)
        enc.pack_optional(self.new_producers)
        enc.pack_list(self.header_extensions)

    @classmethod
    def unpack(cls, dec: Decoder):
        timestamp = dec.unpack_u32()
        producer = dec.unpack_name()
        confirmed = dec.unpack_u16()
        previous = dec.unpack(Checksum256)
        transaction_mroot = dec.unpack(Checksum256)
        action_mroot = dec.unpack(Checksum256)
        schedule_version = dec.unpack_u32()
        new_producers = dec.unpack_optional(ProducerSchedule)
        header_extensions = dec.unpack_list(Pair)
        return cls(timestamp, producer, confirmed, previous, transaction_mroot, action_mroot, schedule_version, new_producers, header_extensions)
    
    def digest(self) -> bytes:
        h = hashlib.sha256()
        h.update(self.get_bytes())
        return h.digest()

    def calculate_id(self) -> Checksum256:
        block_num = self.block_num()
        block_num_bytes = block_num.to_bytes(4, 'big')
        digest = self.digest()
        return Checksum256(block_num_bytes + digest[4:])

    @classmethod
    def unpack_bytes(cls, data: bytes):
        return cls.unpack(Decoder(data))
