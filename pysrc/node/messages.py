from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from .. import eos
from ..bases.packer import Decoder, Encoder
from ..bases.types import I16, I64, U16, U32, U64, Checksum256, PublicKey, Signature
from ..core.packed_transaction import PackedTransaction
from ..core.signed_block import SignedBlock

handshake_message = 0
chain_size_message = 1
go_away_message = 2
time_message = 3
notice_message = 4
request_message = 5
sync_request_message = 6
signed_block_message = 7         # which = 7
packed_transaction_message = 8   # which = 8

class MessageType(Enum):
    handshake = 0
    chain_size = 1
    go_away = 2
    time = 3
    notice = 4
    request = 5
    sync_request = 6
    signed_block = 7         # which = 7
    packed_transaction = 8   # which = 8

# struct handshake_message {
#     uint16_t                   network_version = 0; ///< incremental value above a computed base
#     chain_id_type              chain_id; ///< used to identify chain
#     fc::sha256                 node_id; ///< used to identify peers and prevent self-connect
#     chain::public_key_type     key; ///< authentication key; may be a producer or peer key, or empty
#     int64_t                    time{0}; ///< time message created in nanoseconds from epoch
#     fc::sha256                 token; ///< digest of time to prove we own the private key of the key above
#     chain::signature_type      sig; ///< signature for the digest
#     string                     p2p_address;
#     uint32_t                   last_irreversible_block_num = 0;
#     block_id_type              last_irreversible_block_id;
#     uint32_t                   head_num = 0;
#     block_id_type              head_id;
#     string                     os;
#     string                     agent;
#     int16_t                    generation = 0;
# };

class NetMessage(object):
    msg_type = None

    def pack_message(self):
        """
        Packs the message into a binary format that can be sent over the network.

        Returns:
            A bytes object containing the packed message.
        """
        enc = Encoder()
        enc.pack(self)
        raw_msg = enc.get_bytes()

        enc = Encoder()
        enc.pack_u32(len(raw_msg)+1)
        enc.pack_u8(self.msg_type)
        enc.write_bytes(raw_msg)
        return enc.get_bytes()

class HandshakeMessage(NetMessage):
    msg_type = handshake_message

    def __init__(self, network_version: U16, chain_id: Checksum256, node_id: Checksum256, key: PublicKey, time: I64, token: Checksum256, sig: Signature, p2p_address: str, last_irreversible_block_num: U32, last_irreversible_block_id: Checksum256, head_num: U32, head_id: Checksum256, os: str, agent: str, generation: I16):
        """
        Initializes a new `NetPlugin` object with the specified parameters.

        Args:
            network_version (U16): The network version.
            chain_id (Checksum256): The chain ID.
            node_id (Checksum256): The node ID.
            key (PublicKey): The public key.
            time (I64): The time.
            token (Checksum256): The token.
            sig (Signature): The signature.
            p2p_address (str): The P2P address.
            last_irreversible_block_num (U32): The last irreversible block number.
            last_irreversible_block_id (Checksum256): The last irreversible block ID.
            head_num (U32): The head block number.
            head_id (Checksum256): The head block ID.
            os (str): The operating system.
            agent (str): The agent.
            generation (I16): The generation.

        Returns:
            None
        """
        self.network_version = network_version
        self.chain_id = chain_id
        self.node_id = node_id
        self.key = key
        self.time = time
        self.token = token
        self.sig = sig
        self.p2p_address = p2p_address
        self.last_irreversible_block_num = last_irreversible_block_num
        self.last_irreversible_block_id = last_irreversible_block_id
        self.head_num = head_num
        self.head_id = head_id
        self.os = os
        self.agent = agent
        self.generation = generation

    def __repr__(self):
        return f"""HandshakeMessage(
            network_version: {self.network_version},
            chain_id: {self.chain_id},
            node_id: {self.node_id},
            key: {self.key},
            time: {self.time},
            token: {self.token},
            sig: {self.sig},
            p2p_address: {self.p2p_address},
            last_irreversible_block_num: {self.last_irreversible_block_num},
            last_irreversible_block_id: {self.last_irreversible_block_id},
            head_num: {self.head_num},
            head_id: {self.head_id},
            os: {self.os},
            agent: {self.agent},
            generation: {self.generation}
        )"""

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return (
            self.network_version == other.network_version and
            self.chain_id == other.chain_id and
            self.node_id == other.node_id and
            self.key == other.key and
            self.time == other.time and
            self.token == other.token and
            self.sig == other.sig and
            self.p2p_address == other.p2p_address and
            self.last_irreversible_block_num == other.last_irreversible_block_num and
            self.last_irreversible_block_id == other.last_irreversible_block_id and
            self.head_num == other.head_num and
            self.head_id == other.head_id and
            self.os == other.os and
            self.agent == other.agent and
            self.generation == other.generation
        )
    
    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack_u16(self.network_version)
        enc.pack(self.chain_id)
        enc.pack(self.node_id)
        enc.pack(self.key)
        enc.pack_i64(self.time)
        enc.pack(self.token)
        enc.pack(self.sig)
        enc.pack_string(self.p2p_address)
        enc.pack_u32(self.last_irreversible_block_num)
        enc.pack(self.last_irreversible_block_id)
        enc.pack_u32(self.head_num)
        enc.pack(self.head_id)
        enc.pack_string(self.os)
        enc.pack_string(self.agent)
        enc.pack_i16(self.generation)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        network_version = dec.unpack_u16()
        chain_id = Checksum256.unpack(dec)
        node_id = Checksum256.unpack(dec)
        key = PublicKey.unpack(dec)
        time = dec.unpack_i64()
        token = Checksum256.unpack(dec)
        sig = Signature.unpack(dec)
        p2p_address = dec.unpack_string()
        last_irreversible_block_num = dec.unpack_u32()
        last_irreversible_block_id = Checksum256.unpack(dec)
        head_num = dec.unpack_u32()
        head_id = Checksum256.unpack(dec)
        os = dec.unpack_string()
        agent = dec.unpack_string()
        generation = dec.unpack_i16()
        return cls(
            network_version,
            chain_id,
            node_id,
            key,
            time,
            token,
            sig,
            p2p_address,
            last_irreversible_block_num,
            last_irreversible_block_id,
            head_num,
            head_id,
            os,
            agent,
            generation
        )

    @classmethod
    def unpack_bytes(cls, data: bytes):
        return cls.unpack(Decoder(data))

# struct chain_size_message {
#     uint32_t                   last_irreversible_block_num = 0;
#     block_id_type              last_irreversible_block_id;
#     uint32_t                   head_num = 0;
#     block_id_type              head_id;
# };

class ChainSizeMessage(NetMessage):
    msg_type = chain_size_message

    def __init__(self, last_irreversible_block_num: U32, last_irreversible_block_id: Checksum256, head_num: U32, head_id: Checksum256):
        """
        Represents the current state of the network.

        Args:
            last_irreversible_block_num (int): The block number of the last irreversible block.
            last_irreversible_block_id (bytes): The ID of the last irreversible block.
            head_num (int): The block number of the current head block.
            head_id (bytes): The ID of the current head block.
        """
        self.last_irreversible_block_num = last_irreversible_block_num
        self.last_irreversible_block_id = last_irreversible_block_id
        self.head_num = head_num
        self.head_id = head_id

    def __repr__(self):
        return f"""ChainSizeMessage(
            last_irreversible_block_num: {self.last_irreversible_block_num},
            last_irreversible_block_id: {self.last_irreversible_block_id},
            head_num: {self.head_num},
            head_id: {self.head_id}
        )"""

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return (
            self.last_irreversible_block_num == other.last_irreversible_block_num and
            self.last_irreversible_block_id == other.last_irreversible_block_id and
            self.head_num == other.head_num and
            self.head_id == other.head_id
        )
    
    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack_u32(self.last_irreversible_block_num)
        enc.pack(self.last_irreversible_block_id)
        enc.pack_u32(self.head_num)
        enc.pack(self.head_id)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        last_irreversible_block_num = dec.unpack_u32()
        last_irreversible_block_id = Checksum256.unpack(dec)
        head_num = dec.unpack_u32()
        head_id = Checksum256.unpack(dec)
        return cls(
            last_irreversible_block_num,
            last_irreversible_block_id,
            head_num,
            head_id
        )

    @classmethod
    def unpack_bytes(cls, data: bytes):
        return cls.unpack(Decoder(data))

# enum go_away_reason {
#     no_reason, ///< no reason to go away
#     self, ///< the connection is to itself
#     duplicate, ///< the connection is redundant
#     wrong_chain, ///< the peer's chain id doesn't match
#     wrong_version, ///< the peer's network version doesn't match
#     forked, ///< the peer's irreversible blocks are different
#     unlinkable, ///< the peer sent a block we couldn't use
#     bad_transaction, ///< the peer sent a transaction that failed verification
#     validation, ///< the peer sent a block that failed validation
#     benign_other, ///< reasons such as a timeout. not fatal but warrant resetting
#     fatal_other, ///< a catch-all for errors we don't have discriminated
#     authentication ///< peer failed authenicatio
# };

class GoAwayReason(Enum):
    no_reason = 0
    self_ = 1
    duplicate = 2
    wrong_chain = 3
    wrong_version = 4
    forked = 5
    unlinkable = 6
    bad_transaction = 7
    validation = 8
    benign_other = 9
    fatal_other = 10
    authentication = 11

# struct go_away_message {
#     go_away_message(go_away_reason r = no_reason) : reason(r), node_id() {}
#     go_away_reason reason{no_reason};
#     fc::sha256 node_id; ///< for duplicate notification
# };

class GoAwayMessage(NetMessage):
    msg_type = go_away_message

    def __init__(self, reason: GoAwayReason, node_id: Checksum256):
        """
        Initializes a new GoAwayMessage object with the given reason and node ID.

        Args:
            reason (GoAwayReason): The reason for the GoAway message.
            node_id (Checksum256): The ID of the node that is being disconnected.
        """
        self.reason = reason
        self.node_id = node_id

    def __repr__(self):
        return f"""GoAwayMessage(
            reason: {self.reason},
            node_id: {self.node_id}
        )"""

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return (
            self.reason == other.reason and
            self.node_id == other.node_id
        )
    
    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack_u32(self.reason.value)
        enc.pack(self.node_id)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        reason = GoAwayReason(dec.unpack_u32())
        node_id = Checksum256.unpack(dec)
        return cls(
            reason,
            node_id
        )

    @classmethod
    def unpack_bytes(cls, data: bytes):
        return cls.unpack(Decoder(data))

# struct time_message {
#         int64_t  org{0};       //!< origin timestamp, in nanoseconds
#         int64_t  rec{0};       //!< receive timestamp, in nanoseconds
#         int64_t  xmt{0};       //!< transmit timestamp, in nanoseconds
# mutable int64_t  dst{0};       //!< destination timestamp, in nanoseconds
# };

class TimeMessage(NetMessage):
    """
    A message that contains time synchronization information.
    """
    msg_type = time_message
    def __init__(self, org: I64, rec: I64, xmt: I64, dst: I64):
        """
        Initializes a new TimeMessage object.

        Args:
            org (int): The origin timestamp of the message.
            rec (int): The receive timestamp of the message.
            xmt (int): The transmit timestamp of the message.
            dst (int): The destination timestamp of the message.
        """
        self.org = org
        self.rec = rec
        self.xmt = xmt
        self.dst = dst

    def is_valid(self):
        return not self.xmt == 0

    def __repr__(self):
        return f"""TimeMessage(
            org: {self.org},
            rec: {self.rec},
            xmt: {self.xmt},
            dst: {self.dst}
        )"""

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return (
            self.org == other.org and
            self.rec == other.rec and
            self.xmt == other.xmt and
            self.dst == other.dst
        )
    
    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack_i64(self.org)
        enc.pack_i64(self.rec)
        enc.pack_i64(self.xmt)
        enc.pack_i64(self.dst)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        org = dec.unpack_i64()
        rec = dec.unpack_i64()
        xmt = dec.unpack_i64()
        dst = dec.unpack_i64()
        return cls(
            org,
            rec,
            xmt,
            dst
        )

    @classmethod
    def unpack_bytes(cls, data: bytes):
        return cls.unpack(Decoder(data))

# enum id_list_modes {
#     none,
#     catch_up,
#     last_irr_catch_up,
#     normal
# };

class IdListModes(Enum):
    none = 0
    catch_up = 1
    last_irr_catch_up = 2
    normal = 3

# struct ordered_ids {
#     select_ids() : mode(none),pending(0),ids() {}
#     id_list_modes  mode{none};
#     uint32_t       pending{0};
#     vector<fc::sha256>      ids;
#     bool           empty () const { return (mode == none || ids.empty()); }
# }

class OrderedIds(object):
    def __init__(self, mode: IdListModes, pending: U32, ids: List[Checksum256]):
        self.mode = mode
        self.pending = pending
        self.ids = ids

    def __repr__(self):
        return f"""OrderedIds(
            mode: {self.mode},
            pending: {self.pending},
            ids: {self.ids}
        )"""

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return (
            self.mode == other.mode and
            self.pending == other.pending and
            self.ids == other.ids
        )
    
    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack_u32(self.mode.value)
        enc.pack_u32(self.pending)
        enc.pack_list(self.ids)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        mode = IdListModes(dec.unpack_u32())
        pending = dec.unpack_u32()
        ids = dec.unpack_list(Checksum256)
        return cls(
            mode,
            pending,
            ids
        )

    @classmethod
    def unpack_bytes(cls, data: bytes):
        return cls.unpack(Decoder(data))

# struct request_message {
#     request_message() : req_trx(), req_blocks() {}
#     ordered_txn_ids req_trx;
#     ordered_blk_ids req_blocks;
# }

class RequestMessage(NetMessage):
    """
    A message requesting specific transactions and blocks.
    """
    msg_type = request_message

    def __init__(self, req_trx: OrderedIds, req_blocks: OrderedIds):
        """
        Initializes a new RequestMessage object.

        Args:
            req_trx (OrderedIds): An ordered list of transaction IDs to request.
            req_blocks (OrderedIds): An ordered list of block IDs to request.
        """
        self.req_trx = req_trx
        self.req_blocks = req_blocks

    def __repr__(self):
        return f"""RequestMessage(
            req_trx: {self.req_trx},
            req_blocks: {self.req_blocks}
        )"""

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return (
            self.req_trx == other.req_trx and
            self.req_blocks == other.req_blocks
        )
    
    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack(self.req_trx)
        enc.pack(self.req_blocks)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        req_trx = OrderedIds.unpack(dec)
        req_blocks = OrderedIds.unpack(dec)
        return cls(
            req_trx,
            req_blocks
        )

    @classmethod
    def unpack_bytes(cls, data: bytes):
        return cls.unpack(Decoder(data))

#   struct notice_message {
#     notice_message() : known_trx(), known_blocks() {}
#     ordered_ids known_trx;
#     ordered_ids known_blocks;
#   };

class NoticeMessage(NetMessage):
    """
    A message sent by a node to notify other nodes of known transactions and blocks.
    """
    msg_type = notice_message
    def __init__(self, known_trx: OrderedIds, known_blocks: OrderedIds):
        """
        Initializes a new NoticeMessage object.

        Args:
            known_trx (OrderedIds): A list of transaction IDs known by the node.
            known_blocks (OrderedIds): A list of block IDs known by the node.
        """
        self.known_trx = known_trx
        self.known_blocks = known_blocks

    def __repr__(self):
        return f"""NoticeMessage(
            known_trx: {self.known_trx},
            known_blocks: {self.known_blocks}
        )"""

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return (
            self.known_trx == other.known_trx and
            self.known_blocks == other.known_blocks
        )
    
    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack(self.known_trx)
        enc.pack(self.known_blocks)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        known_trx = OrderedIds.unpack(dec)
        known_blocks = OrderedIds.unpack(dec)
        return cls(
            known_trx,
            known_blocks
        )

    @classmethod
    def unpack_bytes(cls, data: bytes):
        return cls.unpack(Decoder(data))

#    struct sync_request_message {
#       uint32_t start_block{0};
#       uint32_t end_block{0};
#    };

class SyncRequestMessage(NetMessage):
    """
    A message that requests synchronization of blocks between two nodes.
    """
    msg_type = sync_request_message
    def __init__(self, start_block: U32, end_block: U32):
        """
        Initializes a new SyncRequestMessage object.

        Args:
            start_block (U32): The starting block number to synchronize from.
            end_block (U32): The ending block number to synchronize to.
        """
        assert start_block <= end_block
        self.start_block = start_block
        self.end_block = end_block

    def __repr__(self):
        return f"""SyncRequestMessage(start_block: {self.start_block}, end_block: {self.end_block})"""

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        return (
            self.start_block == other.start_block and
            self.end_block == other.end_block
        )
    
    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.pack_u32(self.start_block)
        enc.pack_u32(self.end_block)
        return enc.get_pos() - pos

    @classmethod
    def unpack(cls, dec: Decoder):
        start_block = dec.unpack_u32()
        end_block = dec.unpack_u32()
        return cls(
            start_block,
            end_block
        )

    @classmethod
    def unpack_bytes(cls, data: bytes):
        return cls.unpack(Decoder(data))

# signed_block,         // which = 7
# packed_transaction>;  // which = 8

class SignedBlockMessage(NetMessage):
    msg_type = signed_block_message
    def __init__(self, raw_block: bytes):
        self._raw_block = raw_block
        self._block = None

    @property
    def raw_block(self):
        return self._raw_block
    
    @property
    def block(self):
        if self._block is None:
            self._block = SignedBlock.unpack(self.raw_block)
        return self._block

    def __repr__(self):
        return repr(self.block)
 
    def __str__(self):
        return self.__repr__()
    
    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.write_bytes(self.raw_block)
        return enc.get_pos() - pos

class PackedTransactionMessage(NetMessage):
    msg_type = packed_transaction_message

    def __init__(self, raw_trx: bytes):
        self._raw_trx = raw_trx
        self._trx = None

    @property
    def raw_trx(self):
        return self._raw_trx

    @property
    def trx(self):
        if self._trx is None:
            self._trx = PackedTransaction.unpack(self.raw_trx)
        return self._trx

    def __repr__(self):
        return repr(self.trx)

    def __str__(self):
        return self.__repr__()
    
    def pack(self, enc: Encoder):
        pos = enc.get_pos()
        enc.write_bytes(self.raw_trx)
        return enc.get_pos() - pos

#    using net_message = std::variant<handshake_message,
#                                     chain_size_message,
#                                     go_away_message,
#                                     time_message,
#                                     notice_message,
#                                     request_message,
#                                     sync_request_message,
#                                     signed_block,         // which = 7
#                                     packed_transaction>;  // which = 8
