import asyncio
import io
import logging
import multiprocessing
import secrets
import signal
import socket
import ssl
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from . import debug, eos, log, node_config
from .blocks import BlockHeader
from .chain import Chain
from .chain_exceptions import (DatabaseGuardException, ForkDatabaseException,
                               UnlinkableBlockException)
from .packer import Decoder, Encoder
from .transaction import Transaction
from .types import I16, I64, U16, U32, U64, Checksum256, PublicKey, Signature

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

block_time_window_size = 60 * 12 # 12 Hours
block_count_per_slot = 2 * 60 # one minute per slot
print_sync_blocks_info_interval = 10

default_sync_fetch_span = 300
default_block_latency = 10

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
    def __init__(self, chain: Chain, rwlock = None, peer: str = ''):
        self.peer = peer
        self.chain = chain
        self.rwlock = rwlock
        self.set_default()
        self.goway_listeners = []
        self.last_time_message = None
        self.last_sync_request = None
        self.heart_beat_task = None
        self.last_handshake = None
        self.lock = asyncio.Lock()

        net_config = node_config.get_net_config()
        try:
            self.sync_fetch_span = net_config['sync_fetch_span']
        except KeyError:
            self.sync_fetch_span = default_sync_fetch_span

        try:
            socks5_proxy = net_config['socks5_proxy']
            self.proxy_host, self.proxy_port = socks5_proxy.split(':')
        except KeyError:
            self.proxy_host, self.proxy_port = None, None
        
        self.logger = logging.getLogger(peer)
        self.logger.setLevel(logging.INFO)

        formater = log.ConnectionFormatter(self)
        handler = logging.StreamHandler()
        handler.setFormatter(formater)
        self.logger.addHandler(handler)

    def add_goway_listener(self, listener):
        self.goway_listeners.append(listener)

    def set_default(self):
        self.connected = False
        self.reader = None
        self.writer = None
        # self.last_notice_message = None
        self.time_message_latency = 0.0
        self.generation = 1

        self.busy = True
        self.closed = False
        self.avg_block_time = 0.0
        self.last_handshake_cost_time = 0.0

        self.block_counter = 0
        self.total_bytes = 0

        self.block_counter_start_time: Optional[float] = None
        self.block_times = []
        self.print_block_start_time: Optional[float] = None

    def __repr__(self):
        return f'Connection(peer={self.peer})'

    def __str__(self):
        return self.__repr__()

    def close(self):
        if self.closed:
            self.logger.info(f'+++++++++already closed')
            return
        if self.heart_beat_task:
            self.heart_beat_task.cancel()
            self.heart_beat_task = None
        self.connected = False
        self.closed = True
        self.writer.close()
        self.reader = None

    async def sleep(self, seconds: float):
        while seconds > 0.0:
            await asyncio.sleep(0.1)
            seconds -= 0.1
            if eos.should_exit():
                return

    async def read(self, length):
        if self.closed:
            return None
        try:
            return await self.reader.readexactly(length)
        except asyncio.exceptions.IncompleteReadError as e:
            self.logger.error(f'asyncio.exceptions.IncompleteReadError: len(e.partial)={len(e.partial)}, e.expected={e.expected}')
            self.close()
        return None

    async def read_message(self):
        msg_len = await self.read(4)
        if not msg_len:
            return (None, None)
        msg_len = int.from_bytes(msg_len, 'little')
        if msg_len >= max_package_size or msg_len < 2:
            self.close()
            raise Exception(f'bad message length: {msg_len}')
            return (None, None)

        msg_type = await self.read(1)
        if not msg_type:
            self.logger.error(f'fail to read msg type')
            # self.close()
            return (None, None)
        msg_type = msg_type[0]
        # self.logger.info(f'+++{msg_type}, {msg_len}')
        msg = await self.read(msg_len-1)
        if not msg:
            self.logger.error(f'fail to read msg')
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
            self.logger.error(f'connection error when sending message {msg}')
            self.logger.exception(e)
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
        if self.generation == 0x7fff:
            self.generation = 1
        return msg

    async def handle_time_message(self, message: TimeMessage):
        now_time = int(time.time()*1e9)
        if not message.is_valid():
            self.logger.info(f"invalid time message")
            return False
        if message.org == 0:
            reply_message = TimeMessage(message.xmt, now_time, now_time, 0)
            return await self.send_message(message)
        else:
            if self.last_time_message and self.last_time_message.xmt == message.org:
                message.dst = now_time
                delay = (message.dst - message.org)
                self.logger.info(f"latency: %s", delay)

    async def send_handshake_message(self):
        debug.print_caller_info()
        msg = self.build_handshake_message()
        self.logger.info(f'send handshake message: {msg}')
        return await self.send_message(msg)

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
                self.logger.error(f'handshake timeout')
                return False
            timeout -= (time.monotonic() - start)
            start = time.monotonic()
            if not raw_msg:
                return False
            if tp == time_message:
                message = TimeMessage.unpack_bytes(raw_msg)
                self.logger.info(f"message")
                now_time = int(time.time()*1e9)
                if not message.is_valid():
                    self.logger.info(f"invalid time message")
                    return False
                if msg.xmt == message.org:
                    message.dst = now_time
                    delay = (message.dst - message.org)
                    self.logger.info(f"latency: %s", delay)
                    self.time_message_latency = delay
                    return True
                return False
            else:
                self.logger.error(f"receive message during handshake: {tp}")
        return False

    async def heart_beat(self):
        while not eos.should_exit():
            try:
                await self.sleep(30.0)
                self.logger.info("+++++++++++=heart beat")
                if not self.connected:
                    return
                self.last_time_message = TimeMessage(0, 0, int(time.time()*1e9), 0)
                self.logger.info(f"send time message: {self.last_time_message}")
                if not await self.send_message(self.last_time_message):
                    self.logger.error(f'fail to send time message')
                    return False
                if not self.send_handshake_message():
                    self.logger.error(f'fail to send handshake message')
                    return False
            except ConnectionResetError:
                self.logger.error(f'connection reset')
                break
            except asyncio.exceptions.CancelledError:
                self.logger.info(f"heart beat task CancelledError")
                break

    async def send_sync_request_message(self, start_block: Optional[U32] = None, end_block: Optional[U32] = None):
        module_name, line_num = debug.get_caller_info()
        self.logger.info(f'+++++from: {module_name} at line {line_num}')

        if start_block is None:
            start_block = self.chain.head_block_num() + 1
        if end_block is None:
            if not self.last_handshake:
                self.logger.info(f'+++++no handshake info')
                return True
            end_block = start_block + self.sync_fetch_span - 1
            if end_block > self.last_handshake.head_num:
                end_block = self.last_handshake.head_num
            if end_block < start_block:
                self.logger.info(f'+++++no blocks to sync')
                return await self.send_handshake_message()
        msg = SyncRequestMessage(start_block, end_block)
        self.last_sync_request = msg
        self.logger.info(f"+++++{msg}")
        return await self.send_message(msg)

    async def send_reset_sync_request_message(self):
        debug.print_caller_info()
        self.logger.info('+++++reset sync request')
        msg = SyncRequestMessage(0, 0)
        return await self.send_message(msg)

    async def resync_from_irreversible_block_num_plus_one(self):
        start_block = self.chain.last_irreversible_block_num() + 1
        end_block = self.chain.head_block_num()
        await self.send_sync_request_message(start_block, end_block)

    def reset_block_sync_info(self):
        self.block_counter = 0
        self.total_bytes = 0
        self.block_counter_start_time: Optional[float] = None
        self.block_times = []
        self.print_block_start_time: Optional[float] = None

    def calculate_block_sync_info(self, header: BlockHeader, block_size: int):
        if not self.block_counter_start_time:
            self.block_counter_start_time = time.monotonic()
            return

        self.block_counter += 1
        self.total_bytes += block_size

        if self.block_counter == block_count_per_slot:
            duration = time.monotonic() - self.block_counter_start_time
            self.block_times.append((self.total_bytes, duration))
            if len(self.block_times) >= block_time_window_size:
                self.block_times.pop(0)

            self.block_counter = 0
            self.total_bytes = 0
            self.block_counter_start_time = time.monotonic()

        if not self.print_block_start_time:
            self.print_block_start_time = time.monotonic()

        interval = time.monotonic() - self.print_block_start_time
        if interval < print_sync_blocks_info_interval:
            return

        self.print_block_start_time = time.monotonic()

        if len(self.block_times) == 0:
            return

        total_block_time = 0
        total_block_size = 0
        for info in self.block_times:
            total_block_size += info[0]
            total_block_time += info[1]

        total_blcoks = len(self.block_times) * block_count_per_slot
        block_sync_speed = round(total_blcoks / total_block_time, 1)
        block_sync_network_speed = round(total_block_size / total_block_time / 1024, 1)

        received_block_num: U32 = header.block_num()

        if self.last_handshake and self.last_handshake.head_num > received_block_num:
            remaining_blocks = self.last_handshake.head_num - received_block_num
            total_seconds = remaining_blocks/block_sync_speed

            days, seconds = divmod(total_seconds, 24*60*60)
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            if days > 0.0:
                remaining_time = "{:02}d:{:02}h:{:02}m:{:02}s".format(int(days), int(hours), int(minutes), int(seconds))
            elif hours > 0.0:
                remaining_time = "{:02}h:{:02}m:{:02}s".format(int(hours), int(minutes), int(seconds))
            else:
                remaining_time = "{:02}m:{:02}s".format(int(minutes), int(seconds))
            self.logger.info(f"in sync, estimated remaining time: {remaining_time}, {block_sync_speed} b/s, {block_sync_network_speed} KB/s, current peer, current block num: {received_block_num}, current block time: {header.block_time()}, remaining blocks: {remaining_blocks}")
        else:
            self.logger.info(f"block speed: {block_sync_speed} b/s, current block num: {received_block_num}, current block time: {header.block_time()}")

    async def _handle_message(self):
        tp, raw_msg = await self.read_message()
        if not raw_msg:
            return False
        if tp == handshake_message:
            message = HandshakeMessage.unpack_bytes(raw_msg)
            self.last_handshake = message
            self.logger.info("received handshake message: %s", message)
            if self.chain.head_block_num() < message.last_irreversible_block_num:
                if not await self.send_sync_request_message():
                    return False
            elif self.chain.head_block_id() == message.head_id:
                return True
            elif 0 < message.head_num - self.chain.head_block_num() < default_block_latency:
                req_trx = OrderedIds(IdListModes.none, 0, [])
                req_blocks = OrderedIds(IdListModes.catch_up, 0, [self.chain.head_block_id()])
                msg = RequestMessage(req_trx, req_blocks)
                self.logger.info(f'send request message: {msg}')
                return await self.send_message(msg)
            elif self.chain.head_block_num() > message.head_num:
                ahead_num = self.chain.head_block_num() - message.head_num
                self.logger.info(f"block num is ahead of peer by {ahead_num}")
                return True
            # else:
            #     # last_irr_catch_up catch_up
            #     req_trx = OrderedIds(IdListModes.none, 0, [])
            #     req_blocks = OrderedIds(IdListModes.catch_up, self.chain.head_block_num() + 1, [])
            #     msg = RequestMessage(req_trx, req_blocks)
            #     self.logger.info(msg)
        elif tp == go_away_message:
            message = GoAwayMessage.unpack_bytes(raw_msg)
            self.logger.info(message)
            for listener in self.goway_listeners:
                listener(self, GoAwayMessage.unpack_bytes(raw_msg))
            self.close()
            return False
        elif tp == request_message:
            message = RequestMessage.unpack_bytes(raw_msg)
            self.logger.info(message)
        elif tp == signed_block_message:
            header = BlockHeader.unpack_bytes(raw_msg)
            received_block_num = header.block_num()
            head_block_num = self.chain.head_block_num()
            # self.logger.info(f"++++++++head_block_num: {head_block_num}, received_block_num: {received_block_num}, received_block_time: {header.block_time()}")
            # if received_block_num % 100 == 0:
            #     self.logger.info("++++++++head_block_num: %s, received_block_num: %s", head_block_num, received_block_num)
            if head_block_num >= received_block_num:
                received_block_id = header.calculate_id()
                block_id = self.chain.get_block_id_for_num(received_block_num)
                if block_id == received_block_id:
                    self.logger.info(f"++++++++receive duplicated block: head_block_num: {head_block_num}, received_block_num: {received_block_num}, received block_id: {received_block_id}")
                    return True
                else:
                    self.logger.info(f"++++++++receive invalid block, maybe fork happened: {received_block_num}, block_id: {block_id}, received block_id: {received_block_id}")
            elif head_block_num +1 < received_block_num:
                self.logger.error(f"++++++++++invalid incomming block number: expected: {head_block_num + 1}: received: {received_block_num}")
                if not await self.send_reset_sync_request_message():
                    return False
                req_trx = OrderedIds(IdListModes.none, 0, [])
                req_blocks = OrderedIds(IdListModes.catch_up, 0, [self.chain.head_block_id()])
                msg = RequestMessage(req_trx, req_blocks)
                self.logger.info(f'send request message: {msg}')
                return await self.send_message(msg)

                # if not await self.send_handshake_message():
                #     return False
                # return True
            try:
                if time.time() - header.block_time_ms() / 1000 < 60:
                    return_statistics = True
                else:
                    return_statistics = False

                if self.rwlock:
                    with self.rwlock.wlock():
                        ret, statistics = self.chain.push_block(raw_msg, return_statistics)
                        if statistics:
                            self.logger.info(statistics)
                else:
                    ret, statistics = self.chain.push_block(raw_msg, return_statistics)
                    if statistics:
                        self.logger.info(statistics)

                await asyncio.sleep(0.0)
            # unlinkable_block_exception
            except UnlinkableBlockException as e:
                if not await self.send_reset_sync_request_message():
                    return False
                received_block_id = header.calculate_id()
                self.logger.warning(f"++++++++receive unlinkable block: {received_block_num}, received_block_id: {received_block_id}")
                # return await self.resync_from_irreversible_block_num_plus_one()
                req_trx = OrderedIds(IdListModes.none, 0, [])
                req_blocks = OrderedIds(IdListModes.catch_up, 0, [])
                msg = RequestMessage(req_trx, req_blocks)
                self.logger.info(f'send request message: {msg}')
                return await self.send_message(msg)
            except ForkDatabaseException as e:
                # fork_database_exception
                if e.json()['stack'][0]['format'].startswith('we already know about this block'):
                    self.logger.warning(f"++++++++receive duplicated block: {received_block_num}, block_id: {block_id}")
                    return True
            except DatabaseGuardException as e:
                self.logger.fatal(f"%s", e)
                eos.exit()
                return False
            except Exception as e:
                self.logger.fatal(f"%s", e)
                self.logger.exception(e)
                eos.exit()
                return False

            self.calculate_block_sync_info(header, len(raw_msg))

            # self.logger.info(f"++++++++++self.last_handshake.head_num: {self.last_handshake.head_num}, received_block_num: {received_block_num}")
            if self.last_handshake and self.last_handshake.head_num == received_block_num:
                if not await self.send_handshake_message():
                    return False

            if self.last_sync_request and self.last_sync_request.end_block == received_block_num:
                assert self.last_handshake, "last_handshake is None"
                if self.last_handshake.last_irreversible_block_num > received_block_num:
                    return await self.send_sync_request_message()

                if not await self.send_handshake_message():
                    return False

                # send catch up request
                self.last_sync_request = None #SyncRequestMessage(0, 0)

                req_trx = OrderedIds(IdListModes.none, 0, [])
                req_blocks = OrderedIds(IdListModes.catch_up, 0, [self.chain.head_block_id()])
                msg = RequestMessage(req_trx, req_blocks)
                self.logger.info(f'send request message: {msg}')
                return await self.send_message(msg)
            # elif self.last_handshake and self.last_handshake.head_num == received_block_num:
            #     if not await self.send_handshake_message():
            #         return False

            return True

        elif tp == time_message:
            message = TimeMessage.unpack_bytes(raw_msg)
            # self.logger.info(message)
            await self.handle_time_message(message)
        elif tp == sync_request_message:
            message = SyncRequestMessage.unpack_bytes(raw_msg)
            self.logger.info(message)
            #TODO: create a task to send blocks
        elif tp == notice_message:
            message = NoticeMessage.unpack_bytes(raw_msg)
            self.logger.info(f"receive notice message: {message}")

            if message.known_blocks.mode == IdListModes.catch_up:
                pending = message.known_blocks.pending
                try:
                    block_id = message.known_blocks.ids[0]
                    # ret = self.chain.fetch_block_by_id(block_id.to_string())
                    # self.logger.info(f"++++++++++fetch block by id: {block_id}, ret: {ret}")
                except IndexError:
                    msg = GoAwayMessage(GoAwayReasonEnum.no_reason, "no blocks in notice message")
                    for listener in self.goway_listeners:
                        listener(self, msg)
                    await self.send_message(msg)
                    return False

                req_trx = OrderedIds(IdListModes.none, 0, [])
                req_blocks = OrderedIds(IdListModes.catch_up, 0, [self.chain.head_block_id()])
                msg = RequestMessage(req_trx, req_blocks)
                self.logger.info(f'send request message: {msg}')
                return await self.send_message(msg)

                my_block_id = self.chain.get_block_id_for_num(pending)
                if my_block_id and my_block_id == block_id:
                    return await self.send_handshake_message()
                else:
                    req_trx = OrderedIds(IdListModes.none, 0, [])
                    req_blocks = OrderedIds(IdListModes.catch_up, 0, [self.chain.head_block_id()])
                    msg = RequestMessage(req_trx, req_blocks)
                    self.logger.info(f'{msg}')
                    return await self.send_message(msg)
            elif message.known_blocks.mode  == IdListModes.last_irr_catch_up:
                pending = message.known_blocks.pending
                start_block = self.chain.head_block_num() + 1
                if start_block > pending:
                    self.logger.info(f"++++++++++already in sync, start_block: {start_block}, pending: {pending}")
                    return True
                msg = SyncRequestMessage(0, 0)
                self.logger.info('+++++reset sync request before sending sync request when process notice_message')
                if not await self.send_message(msg):
                    return False
                return await self.send_sync_request_message(start_block, pending)
        elif tp == packed_transaction_message:
            # TODO: handle packed transaction message
            # message = PackedTransactionMessage.unpack_bytes(raw_msg)
            pass
        else:
            self.logger.info("++++%s %s", tp, raw_msg)
        return True

    async def handle_messages(self):
        self.last_sync_request = None
        # reset sync request cache in peer in case of lost connection during sync
        await self.send_reset_sync_request_message()

        if not await self.send_handshake_message():
            self.logger.info(f'send handshake message to failed')
            return False

        # if not await self.send_sync_request_message():
        #     self.logger.info(f'send sync request message to failed')
        #     return False

        while not eos.should_exit():
            try:
                if not await self._handle_message():
                    return False
            except Exception as e:
                self.logger.exception(e)
                return False

class OutConnection(Connection):
    def __init__(self, chain: Chain, rwlock = None, peer: str = ''):
        super().__init__(chain, rwlock, peer)
        self.set_default()

    async def open_connection_socks5(self, proxy_host, proxy_port, target_host, target_port):
        # Resolve proxy address and target address
        proxy_addr = socket.gethostbyname(proxy_host)
        target_addr = socket.gethostbyname(target_host)
        target_port = int(target_port)

        reader, writer = await asyncio.open_connection(proxy_addr, proxy_port)

        # Send SOCKS5 greeting message
        writer.write(b"\x05\x01\x00")
        await writer.drain()

        # Receive SOCKS5 server response
        version, method = await reader.readexactly(2)

        # Send SOCKS5 connection request
        writer.write(b"\x05\x01\x00\x01" + socket.inet_aton(target_addr) + target_port.to_bytes(2, 'big'))
        await writer.drain()

        # Receive SOCKS5 server response
        version, rep, rsv, atyp = await reader.readexactly(4)
        if atyp == 1:
            bnd_addr = socket.inet_ntoa(await reader.readexactly(4))
        else:
            bnd_addr = await reader.readexactly(await reader.readexactly(1)[0])
        bnd_port = int.from_bytes(await reader.readexactly(2), 'big')

        if rep != 0:
            writer.close()
            await writer.wait_closed()
            raise Exception(f"SOCKS5 connect request failed with code {rep}")

        return reader, writer

    async def _connect(self):
        self.set_default()
        self.logger.info('connecting to %s', self.peer)
        try:
            host, port = self.peer.split(':')
            if port in ('443', 443):
                self.logger.info('+++++++connect to ssl')
                context = ssl.create_default_context()
                self.reader, self.writer = await asyncio.open_connection(host, port, ssl=context, limit=100*1024*1024)
            else:
                if self.proxy_host:
                    self.reader, self.writer = await self.open_connection_socks5(self.proxy_host, self.proxy_port, host, port)
                else:
                    self.reader, self.writer = await asyncio.open_connection(host, port, limit=100*1024*1024)
            if await self.estimate_connection_latency():
                return self
            return None
        except Exception as e:
            self.logger.info(f'connect to error:')
            self.logger.exception(e)
        return None

    async def connect(self):
        if self.connected:
            return self

        async with self.lock:
            ret = await self._connect()
        if not ret:
            self.closed = True
            self.connected = False
        else:
            self.connected = True
            if self.heart_beat_task:
                self.heart_beat_task.cancel()
                self.heart_beat_task = asyncio.create_task(self.heart_beat())
        self.busy = False
        return ret

# print(os.getpid())
# input('press enter to continue')

class Network(object):
    def __init__(self, chain, peers: List[str], rwlock: Optional[multiprocessing.Lock] = None):
        self.chain = chain
        self.connections: List[Connection] = []
        self.generation = 0
        self.last_time_message = None
        self.peers = peers
        self.sync_tasks = {}
        self.unfinished_sync_requests = []
        self.sync_finished = False
        self.conn: Optional[Connection] = None

        self.logger = log.get_logger('network')

        self.rwlock = rwlock

    async def retry_connection(self):
        while not eos.should_exit():
            await self.sleep(30.0)
            for conn in self.connections:
                if conn.connected:
                    continue
                self.logger.info(f'retry connection to {conn.peer}')
                await conn.connect()

    def on_goway(self, conn: Connection, msg: GoAwayMessage):
        self.logger.info(f'connection {conn.peer} sent a go away message: {msg}')
        try:
            self.connections.remove(conn)
        except ValueError:
            self.logger.info(f'{conn.peer} not in connections')
            pass

        # try:
        #     self.peers.remove(conn.peer)
        # except ValueError:
        #     self.logger.info(f'peer {conn.peer} not in peers')
        #     pass

    async def _init(self):
        if not self.connections:
            asyncio.create_task(self.retry_connection())
            for peer in self.peers:
                conn = OutConnection(self.chain, self.rwlock, peer)
                conn.add_goway_listener(self.on_goway)
                self.connections.append(conn)

        for c in self.connections:
            if c.connected:
                return True

        for c in self.connections:
            if c.connected:
                return True

        has_connected = False
        while not has_connected and not eos.should_exit():
            tasks = []
            for conn in self.connections:
                task = asyncio.create_task(conn.connect())
                tasks.append(task)

            for task in tasks:
                conn = await task
                if not conn:
                    continue
                has_connected = True
                self.logger.info(f'connected to {conn.peer}')
            if not has_connected:
                self.logger.info('+++++++no connection, sleep 10s')
                await self.sleep(10.0)
        return True

    async def sleep(self, seconds: float):
        while seconds > 0.0:
            await asyncio.sleep(0.1)
            seconds -= 0.1
            if eos.should_exit():
                return

    async def init(self):
        while not eos.should_exit():
            try:
                if await self._init():
                    self.logger.info('+++++++_init success')
                    return True
            except Exception as e:
                self.logger.exception(e)
            await self.sleep(10.0)
        
    async def get_fastest_connection(self):
        connections = [c for c in self.connections if c.connected]
        if not connections:
            while not eos.should_exit():
                await self.init()
                connections = [c for c in self.connections if c.connected]
                if connections:
                    break
                self.logger.info('+++++++no connection')
                await self.sleep(10.0)

        conn = connections[0]
        for c in connections[1:]:
            if c.time_message_latency < conn.time_message_latency:
                conn = c
        return conn

    async def _run(self):
        await self.init()

        while not eos.should_exit():
            try:
                self.conn = await self.get_fastest_connection()
                self.logger.info('+++++choose fastest connection: %s', self.conn.peer)
                await self.conn.handle_messages()
                await self.sleep(3.0)
            except Exception as e:
                self.logger.exception(e)
                self.sleep(5.0)

        return False

    async def run(self):
        while not eos.should_exit():
            try:
                ret = await self._run()
                if not ret:
                    break
            except asyncio.exceptions.CancelledError:
                self.chain.free()
                break
            except Exception as e:
                self.logger.info(type(e))
                self.logger.exception(e)
                break
        self.logger.info('network exit')

    async def get_connection(self, timeout: float = 10.0):
        while not self.conn and timeout > 0.0:
            await asyncio.sleep(0.1)
            timeout -= 0.1
        return self.conn
