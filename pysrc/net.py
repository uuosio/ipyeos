import asyncio
from enum import Enum
import io
import ssl
import time
import secrets
import signal
from typing import List, Dict, Type, Union, Any, Optional

from .blocks import BlockHeader
from .packer import Encoder, Decoder
from .types import I16, U16, U32, I64, U64, PublicKey, Signature, Checksum256
from . import log
from .transaction import Transaction
from .chain import Chain

handshake_message = 0
chain_size_message = 1
go_away_message = 2
time_message = 3
notice_message = 4
request_message = 5
sync_request_message = 6
signed_block_message = 7         # which = 7
packed_transaction_message = 8   # which = 8
genesis_state = 9
abi_def = 10
transaction_type = 11
global_property_type = 12

net_version_base = 0x04b5
net_version_range = 106

block_time_window_size = 60 * 24 # one day
block_count_per_slot = 2*60 # one minute per slot

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

logger = log.get_logger(__name__)

max_package_size = 5*1024*1024

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

class GoAwayReadon(Enum):
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

    def __init__(self, reason: GoAwayReadon, node_id: Checksum256):
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
        reason = GoAwayReadon(dec.unpack_u32())
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
            self._block = eos.unpack_native_object(signed_block, self.raw_block)
        return self._block

    def __repr__(self):
        return self.block
 
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
        return self._trx

    def __repr__(self):
        if self.trx is None:
            self.trx = eos.unpack_native_object(transaction_v0, self.raw_trx)
        return trx
    
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

class SyncBlockInfo(object):
    def __init__(self, conn = None, task = None, start_block = 0, end_block = 0):
        self.conn = conn
        self.task = task
        self.start_block = start_block
        self.end_block = end_block
        self.current_block = start_block

    def __repr__(self):
        return f'SyncBlockInfo(conn={self.conn}, start_block={self.start_block}, end_block={self.end_block}, current_block={self.current_block})'

    def __str__(self):
        return self.__repr__()

class Connection(object):
    def __init__(self, chain: Chain, peer: str = ''):
        self.peer = peer
        self.chain = chain
        self.set_default()
        self.goway_listeners = []
        self.last_time_message = None
        self.last_sync_request = None
        self.heart_beat_task = None

    def add_goway_listener(self, listener):
        self.goway_listeners.append(listener)

    def set_default(self):
        self.connected = False
        self.reader = None
        self.writer = None
        self.last_handshake = None
        # self.last_notice_message = None
        self.time_message_latency = 0.0
        self.generation = 0

        self.busy = True
        self.closed = False
        self.avg_block_time = 0.0
        self.last_handshake_cost_time = 0.0

        self.block_counter = 0
        self.block_counter_start_time: Optional[float] = None
        self.block_times = []
        self.print_block_start_time: Optional[float] = None

    def __repr__(self):
        return f'Connection(peer={self.peer})'

    def __str__(self):
        return self.__repr__()

    def close(self):
        if self.closed:
            logger.info(f'+++++++++{self.peer} already closed')
            return
        self.connected = False
        self.closed = True
        self.writer.close()
        self.reader = None

    async def read(self, length):
        if self.closed:
            return None
        buffer = io.BytesIO()
        while True:
            try:
                data = await self.reader.read(length)
                if not data:
                    self.close()
                    logger.error(f'error reading {length} bytes of data from {self.peer}')
                    return None
                buffer.write(data)
                length -= len(data)
                if length <= 0:
                    break
            except Exception as e:
                logger.exception(e)
                self.close()
                return None
        return buffer.getvalue()

    async def read_message(self):
        msg_len = await self.read(4)
        if not msg_len:
            return (None, None)
        msg_len = int.from_bytes(msg_len, 'little')
        if msg_len >= max_package_size or msg_len < 2:
            self.close()
            raise Exception(f'{self.peer} bad message length: {msg_len}')
            return (None, None)

        msg_type = await self.read(1)
        if not msg_type:
            logger.error(f'{self.peer} fail to read msg type')
            # self.close()
            return (None, None)
        msg_type = msg_type[0]
        # logger.info(f'+++{msg_type}, {msg_len}')
        msg = await self.read(msg_len-1)
        if not msg:
            logger.error(f'{self.peer} fail to read msg')
            # self.close()
            return (None, None)
        return msg_type, msg

    def write(self, data):
        if self.closed:
            return

        if not self.writer:
            return

        self.writer.write(data)

    async def send_message(self, msg: NetMessage):
        try:
            self.write(msg.pack_message())
            await self.writer.drain()
            return True
        except Exception as e:
            logger.error(f'{self.peer} connection error when sending message {msg}')
            logger.exception(e)
            self.close()
            return False

    def build_handshake_message(self):
        msg = HandshakeMessage(
            network_version=net_version_base + 7,
            chain_id=self.chain.chain_id(),
            node_id=Checksum256(secrets.token_bytes(32)),
            key=PublicKey.empty(),
            time=int(time.time()*1e9),
            token=Checksum256.empty(),
            sig=Signature.empty(),
            p2p_address=f'127.0.0.1:9876',
            last_irreversible_block_num=self.chain.last_irreversible_block_num(),
            last_irreversible_block_id=self.chain.last_irreversible_block_id(),
            head_num=self.chain.head_block_num(),
            head_id=self.chain.head_block_id(),
            os='Linux',
            agent='EOS Agent',
            generation=self.generation
        )
        self.generation += 1
        return msg

    async def handle_time_message(self, message: TimeMessage):
        now_time = int(time.time()*1e9)
        if not message.is_valid():
            logger.info(f"{self.peer} invalid time message")
            return False
        if message.org == 0:
            reply_message = TimeMessage(message.xmt, now_time, now_time, 0)
            await self.send_message(message)
        else:
            if self.last_time_message and self.last_time_message.xmt == message.org:
                message.dst = now_time
                delay = (message.dst - message.org)
                logger.info(f"{self.peer} latency: %s", delay)

    async def send_handshake_message(self):
        msg = self.build_handshake_message()
        return await self.send_message(msg)

    async def handshake(self):
        start_time = time.monotonic()
        if not await self.send_handshake_message():
            logger.info(f'{self.peer} fail to send handshake message')
            return False

        timeout = 30.0
        start = time.time()
        while timeout > 0.0:
            try:
                tp, raw_msg = await asyncio.wait_for(self.read_message(), timeout=timeout)
                if not raw_msg:
                    return False
            except asyncio.TimeoutError:
                logger.error(f'{self.peer} handshake timeout')
                return False
            timeout -= (time.time() - start)
            start = time.time()
            if not raw_msg:
                return False
            if tp == handshake_message:
                message = HandshakeMessage.unpack_bytes(raw_msg)
                self.last_handshake = message
                logger.info(f"{self.peer} received handshake message: {message}")
                self.last_handshake_cost_time = time.monotonic() - start_time
                # asyncio.create_task(self.heart_beat())
                return True
            elif tp == notice_message:
                message = NoticeMessage.unpack_bytes(raw_msg)
                logger.info(message)
                # self.last_notice_message = message
                if message.known_blocks.mode in (IdListModes.last_irr_catch_up, IdListModes.catch_up):
                    self.last_handshake_cost_time = time.monotonic() - start_time
                    # pending = message.known_blocks.pending
                    # msg = SyncRequestMessage(self.chain.head_block_num() + 1, pending)
                    # logger.info("+++++send sync request message %s", msg)
                    # await self.send_message(msg)
                    return True
            elif tp == go_away_message:
                for listener in self.goway_listeners:
                    listener(self, GoAwayMessage.unpack_bytes(raw_msg))
                self.close()
                return False
            elif tp == time_message:
                message = TimeMessage.unpack_bytes(raw_msg)
                # logger.info(message)
                await self.handle_time_message(message)
            else:
                logger.error(f"{self.peer} receive message during handshake: {tp}")
        return False

    async def estimate_connection_latency(self):
        msg = TimeMessage(0, 0, int(time.time()*1e9), 0)
        if not await self.send_message(msg):
            return False

        timeout = 30.0
        start = time.monotonic()
        while timeout > 0.0:
            try:
                tp, raw_msg = await asyncio.wait_for(self.read_message(), timeout=timeout)
                if not raw_msg:
                    return False
            except asyncio.TimeoutError:
                logger.error(f'{self.peer} handshake timeout')
                return False
            timeout -= (time.monotonic() - start)
            start = time.monotonic()
            if not raw_msg:
                return False
            if tp == time_message:
                message = TimeMessage.unpack_bytes(raw_msg)
                now_time = int(time.time()*1e9)
                if not message.is_valid():
                    logger.info(f"{self.peer} invalid time message")
                    return False
                if msg.xmt == message.org:
                    message.dst = now_time
                    delay = (message.dst - message.org)
                    logger.info(f"{self.peer} latency: %s", delay)
                    self.time_message_latency = delay
                    return True
                return False
            else:
                logger.error(f"{self.peer} receive message during handshake: {tp}")
        return False

    async def estimate_peer_speed(self):
        start_time = time.monotonic()
        start_block = 2
        end_block = start_block + 10 - 1
        current_block = start_block
        msg = SyncRequestMessage(start_block, end_block)
        try:
            if not await self.send_message(msg):
                return False
        except asyncio.CancelledError as e:
            logger.info(f"{self.peer} CancelledError in request blocks")
            return False
        except Exception as e:
            logger.exception(e)
            return False

        while current_block <= end_block:
            try:
                tp, raw_msg = await self.read_message()
                if not raw_msg:
                    return info
                if tp == signed_block_message:
                    header = BlockHeader.unpack_bytes(raw_msg)
                    received_block_num = header.block_num()
                    if not current_block == received_block_num:
                        logger.error(f'received block num {received_block_num} not equal to current block num {current_block}')
                    current_block += 1
                elif tp == go_away_message:
                    for listener in self.goway_listeners:
                        listener(self, GoAwayMessage.unpack_bytes(raw_msg))
                    self.close()
                    return False
            except Exception as e:
                logger.error(f'{self.peer} error when receiving blocks')
                logger.exception(e)
                return False
            except asyncio.CancelledError as e:
                logger.info(f"{self.peer} CancelledError in request blocks")
                return False
        self.avg_block_time = (time.monotonic() - start_time) / 10
        return True

    async def heart_beat(self):
        while True:
            try:
                await asyncio.sleep(30.0)
                self.last_time_message = TimeMessage(0, 0, int(time.time()*1e9), 0)
                if not self.connected:
                    return
                if not await self.send_message(self.last_time_message):
                    logger.error(f'{self.peer} fail to send time message')
                    return False
            except ConnectionResetError:
                logger.error(f'{self.peer} connection reset')
                break
            except asyncio.exceptions.CancelledError:
                logger.info(f"{self.peer} CancelledError")
                break

    async def send_sync_request_message(self, start_block: Optional[U32] = None, end_block: Optional[U32] = None):
        if start_block is None:
            start_block = self.chain.head_block_num() + 1
        if end_block is None:
            end_block = start_block + 1000 - 1
            if end_block > self.last_handshake.head_num:
                end_block = self.last_handshake.head_num
            if end_block < start_block:
                logger.error(f'{self.peer} no blocks to sync')
                # self.last_sync_request = None
                return True
        msg = SyncRequestMessage(start_block, end_block)
        self.last_sync_request = msg
        logger.info("+++++send sync request message %s", msg)
        return await self.send_message(msg)

    async def resync_from_irreversible_block_num_plus_one(self):
        start_block = self.chain.last_irreversible_block_num() + 1
        end_block = self.chain.head_block_num()
        await self.send_sync_request_message(start_block, end_block)

    def reset_block_sync_info(self):
        self.block_counter = 0
        self.block_counter_start_time: Optional[float] = None
        self.block_times = []
        self.print_block_start_time: Optional[float] = None

    def calculate_block_sync_info(self, header: BlockHeader):
        if not self.block_counter_start_time:
            self.block_counter_start_time = time.monotonic()
            return

        self.block_counter += 1
        if self.block_counter == block_count_per_slot:
            duration = time.monotonic() - self.block_counter_start_time
            self.block_times.append(duration)
            if len(self.block_times) >= block_time_window_size:
                self.block_times.pop(0)

            self.block_counter = 0
            self.block_counter_start_time = time.monotonic()

        if not self.print_block_start_time:
            self.print_block_start_time = time.monotonic()

        interval = time.monotonic() - self.print_block_start_time
        if interval < 30:
            return

        self.print_block_start_time = time.monotonic()

        if len(self.block_times) == 0:
            return

        total_block_time = sum(self.block_times)
        total_blcoks = len(self.block_times) * block_count_per_slot
        block_sync_speed = round(total_blcoks / total_block_time, 1)

        received_block_num: U32 = header.block_num()

        if self.last_handshake and self.last_handshake.head_num > received_block_num:
            remain_blocks = self.last_handshake.head_num - received_block_num
            remain_time = round(remain_blocks/block_sync_speed/60/60, 2)
            logger.info(f"current peer: {self.peer}, current block num: {received_block_num}, current block time: {header.block_time()}, remaining blocks: {remain_blocks}, block sync speed: {block_sync_speed} b/s, estimated remaining time: {remain_time} hours")
        else:
            logger.info(f"current peer: {self.peer}, current block num: {received_block_num}, current block time: {header.block_time()}, block speed: {block_sync_speed} b/s")

    async def _handle_message(self):
        tp, raw_msg = await self.read_message()
        if not raw_msg:
            return False
        if tp == handshake_message:
            message = HandshakeMessage.unpack_bytes(raw_msg)
            self.last_handshake = message
            logger.info("received handshake message: %s", message)
            if self.chain.head_block_num() + 2 < message.head_num:
                logger.info('send_sync_request_message')
                if not await self.send_sync_request_message():
                    return False
            # else:
            #     # last_irr_catch_up catch_up
            #     req_trx = OrderedIds(IdListModes.none, 0, [])
            #     req_blocks = OrderedIds(IdListModes.catch_up, self.chain.head_block_num() + 1, [])
            #     msg = RequestMessage(req_trx, req_blocks)
            #     logger.info(msg)
        elif tp == go_away_message:
            message = GoAwayMessage.unpack_bytes(raw_msg)
            logger.info(message)
            for listener in self.goway_listeners:
                listener(self, GoAwayMessage.unpack_bytes(raw_msg))
            self.close()
            return False
        elif tp == request_message:
            message = RequestMessage.unpack_bytes(raw_msg)
            logger.info(message)
        elif tp == signed_block_message:
            header = BlockHeader.unpack_bytes(raw_msg)
            received_block_num = header.block_num()
            # logger.info(f"{self.peer}: ++++++++received block num: {received_block_num}, block_id: {block_id}")
            head_block_num = self.chain.head_block_num()
            # logger.info(f"{self.peer}: ++++++++head_block_num: {head_block_num}, received_block_num: {received_block_num}")
            # if received_block_num % 100 == 0:
            #     logger.info("++++++++head_block_num: %s, received_block_num: %s", head_block_num, received_block_num)
            if head_block_num >= received_block_num:
                received_block_id = header.calculate_id()
                block_id = self.chain.get_block_id_for_num(received_block_num)
                if block_id == received_block_id:
                    logger.warning(f"{self.peer}: ++++++++receive dumplicated block: head_block_num: {head_block_num}, received_block_num: {received_block_num}, received block_id: {received_block_id}")
                    return True
                else:
                    logger.info(f"{self.peer}: ++++++++receive invalid block, maybe fork happened: {received_block_num}, block_id: {block_id}, received block_id: {received_block_id}")
            elif head_block_num +1 < received_block_num:
                logger.info("++++++++++invalid incomming block number: expected: %s: received: %s", head_block_num + 1, received_block_num)
                if not await self.send_handshake_message():
                    return False
                return True
            try:
                ret = self.chain.push_raw_block(raw_msg)
            except Exception as e:
                # fork_database_exception
                # unlinkable_block_exception
                exception = e.args[0]
                if exception['name'] == 'unlinkable_block_exception':
                    logger.warning(f"{self.peer}: ++++++++receive unlinkable block: {received_block_num}, block_id: {block_id}")
                    await self.resync_from_irreversible_block_num_plus_one()
                    return True
                elif exception['name'] == 'fork_database_exception' and exception['stack'][0]['format'].startswith('we already know about this block'):
                    logger.warning(f"{self.peer}: ++++++++receive dumplicated block: {received_block_num}, block_id: {block_id}")
                    return True
                logger.info(e)
                raise e

            self.calculate_block_sync_info(header)

            if self.last_handshake and self.last_handshake.head_num == received_block_num:
                # await asyncio.sleep(3.0)
                msg = self.build_handshake_message()
                await self.send_message(msg)
                # self.last_sync_request = None
                self.reset_block_sync_info()
                logger.info(f"++++++++++++++sync to head block num {received_block_num} in handshake finished, send handshake message: %s", msg)
            elif self.last_sync_request and self.last_sync_request.end_block == received_block_num:
                logger.info('send_sync_request_message')
                if not await self.send_sync_request_message():
                    return False

        elif tp == time_message:
            message = TimeMessage.unpack_bytes(raw_msg)
            # logger.info(message)
            await self.handle_time_message(message)
        elif tp == sync_request_message:
            message = SyncRequestMessage.unpack_bytes(raw_msg)
            logger.info(message)
            #TODO: create a task to send blocks
        elif tp == notice_message:
            message = NoticeMessage.unpack_bytes(raw_msg)
            logger.info(f"{self.peer}: {message}")

            # TODO: verify catch_up
            # if message.known_blocks.mode == IdListModes.catch_up:
            #     req_trx = OrderedIds(IdListModes.none, 0, [])
            #     req_blocks = OrderedIds(IdListModes.catch_up, 0, [self.chain.head_block_id()])
            #     msg = RequestMessage(req_trx, req_blocks)
            #     logger.info(msg)
            #     self.send_message(msg)

            if message.known_blocks.mode in (IdListModes.last_irr_catch_up, IdListModes.catch_up):
                pending = message.known_blocks.pending
                start_block = self.chain.head_block_num() + 1
                if start_block > pending:
                    logger.info(f"++++++++++already in sync, start_block: {start_block}, pending: {pending}")
                    return True
                msg = SyncRequestMessage(start_block, pending)
                logger.info("+++++send sync request message %s", msg)
                await self.send_message(msg)
        elif tp == packed_transaction_message:
            # TODO: handle packed transaction message
            # message = PackedTransactionMessage.unpack_bytes(raw_msg)
            pass
        else:
            logger.info("++++%s %s", tp, raw_msg)
        return True

    async def handle_messages(self):
        if not self.heart_beat_task or self.heart_beat_task.done():
            self.heart_beat_task = asyncio.create_task(self.heart_beat())

        if not await self.send_handshake_message():
            logger.info(f'send handshake message to {self.peer} failed')
            return False
        # if not await self.send_sync_request_message():
        #     logger.info(f'send sync request message to {self.peer} failed')
        #     return False

        while True:
            try:
                if not await self._handle_message():
                    return False
            except Exception as e:
                logger.exception(e)
                return False

class OutConnection(Connection):
    def __init__(self, chain: Chain, peer: str = ''):
        super().__init__(chain, peer)
        self.peer = peer
        self.chain = chain
        self.set_default()

    async def _connect(self):
        self.set_default()
        logger.info('connecting to %s', self.peer)
        try:
            host, port = self.peer.split(':')
            if port in ('443', 443):
                logger.info('+++++++connect to ssl')
                context = ssl.create_default_context()
                self.reader, self.writer = await asyncio.open_connection(host, port, ssl=context, limit=100*1024*1024)
            else:
                self.reader, self.writer = await asyncio.open_connection(host, port, limit=100*1024*1024)

            # if await self.handshake():
            #     logger.info('handshake success')
            # else:
            #     logger.info(f'connect to {self.peer} failed')
            #     return None
            # if await self.estimate_peer_speed():
            #     logger.info('average block time: %s', self.avg_block_time)
            #     return self
            if await self.estimate_connection_latency():
                return self
            return None
        except Exception as e:
            logger.info(f'connect to {self.peer} error:')
            logger.exception(e)
        return None

    async def connect(self):
        ret = await self._connect()
        if not ret:
            self.closed = True
            self.connected = False
        else:
            self.connected = True
        self.busy = False
        return ret

# print(os.getpid())
# input('press enter to continue')

class Network(object):
    def __init__(self, chain, peers: List[str]):
        self.chain = chain
        self.connections: List[Connection] = []
        self.generation = 1
        self.last_time_message = None
        self.peers = peers
        self.sync_tasks = {}
        self.unfinished_sync_requests = []
        self.sync_finished = False
        self.conn: Optional[Connection] = None

    def on_goway(self, conn: Connection, msg: GoAwayMessage):
        logger.info(f'connection {conn.peer} sent a go away message: {msg}')
        try:
            self.connections.remove(conn)
        except ValueError:
            logger.info(f'{conn.peer} not in connections')
            pass

        # try:
        #     self.peers.remove(conn.peer)
        # except ValueError:
        #     logger.info(f'peer {conn.peer} not in peers')
        #     pass

    async def _init(self):
        self.connections = []
        tasks = []
        for peer in self.peers:
            conn = OutConnection(self.chain, peer)
            conn.add_goway_listener(self.on_goway)
            task = asyncio.create_task(conn.connect())
            tasks.append(task)

        for task in tasks:
            conn = await task
            if not conn:
                continue
            logger.info(f'connected to {conn.peer}, handshake time: {conn.last_handshake_cost_time}, average block time: {conn.avg_block_time}')
            self.connections.append(conn)

        if self.connections:
            return True
        return False

    async def init(self):
        while True:
            try:
                if await self._init():
                    logger.info('+++++++_init success')
                    return True
            except Exception as e:
                logger.exception(e)
            await asyncio.sleep(10.0)
        
    async def get_fastest_connection(self):
        connections = [c for c in self.connections if c.connected]
        if not connections:
            while True:
                await self.init()
                connections = [c for c in self.connections if c.connected]
                if connections:
                    for c in connections:
                        logger.info('++++++connection: %s, time_message_latency: %s', c.peer, c.time_message_latency)
                    break
                logger.error('no available connection')
                await asyncio.sleep(10.0)

        conn = connections[0]
        for c in connections[1:]:
            if not c.connected:
                continue
            if c.time_message_latency < conn.time_message_latency:
                conn = c
        return conn

    async def _run(self):
        head_block_num = 0
        await self.init()

        while True:
            try:
                self.conn = await self.get_fastest_connection()
                logger.info('+++++choose fastest connection: %s', self.conn.peer)
                await self.conn.handle_messages()
            except Exception as e:
                logger.exception(e)
                asyncio.sleep(5.0)

        return False

    async def handle_signal(self, signum):
        logger.info("+++++++handle signal: %s", signum)
        loop = asyncio.get_running_loop()
        for task in asyncio.all_tasks(loop):
            task.cancel()

    async def run(self):
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(self.handle_signal(signal.SIGINT)))
        loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(self.handle_signal(signal.SIGTERM)))

        while True:
            try:
                ret = await self._run()
                if not ret:
                    break
            except asyncio.CancelledError:
                self.chain.free()
                break
            except Exception as e:
                logger.info(type(e))
                logger.exception(e)
                break

    def start(self):
        try:
            asyncio.run(self.run())
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")
