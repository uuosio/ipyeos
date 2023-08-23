import asyncio
import logging
import secrets
import socket
import ssl
import time
from typing import Optional

from . import node_config
from .messages import (
    MessageType,
    NetMessage,
    HandshakeMessage,
    ChainSizeMessage,
    GoAwayReason,
    GoAwayMessage,
    TimeMessage,
    IdListModes,
    OrderedIds,
    RequestMessage,
    NoticeMessage,
    SyncRequestMessage,
    SignedBlockMessage,
    PackedTransactionMessage,
)

from .. import eos
from ..bases import debug, log, utils
from ..bases.types import I16, I64, U16, U32, U64, Checksum256, PublicKey, Signature
from ..core.blocks import BlockHeader
from ..core.chain import Chain
from ..core.chain_exceptions import (DatabaseGuardException, ForkDatabaseException,
                               UnlinkableBlockException)

max_package_size = 5*1024*1024
default_sync_fetch_span = 300
default_block_latency = 1

net_version_base = 0x04b5
net_version_range = 106

block_time_window_size = 60 * 12 # 12 Hours
block_count_per_slot = 2 * 60 # one minute per slot

print_sync_blocks_info_interval = 10

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
        self.sync_request_task = None
        self.sync_task = None

        try:
            self.has_producer = node_config.get_producer_config()
        except:
            self.has_producer = False

        try:
            net_config = node_config.get_net_config()
            self.sync_fetch_span = net_config['sync_fetch_span']
        except:
            self.sync_fetch_span = default_sync_fetch_span

        try:
            net_config = node_config.get_net_config()
            socks5_proxy = net_config['socks5_proxy']
            self.proxy_host, self.proxy_port = socks5_proxy.split(':')
        except:
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
        if self.writer:
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
            if tp == MessageType.time.value:
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
                if not await self.send_handshake_message():
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

    def push_block(self, raw_block: bytes, return_statistics: bool = False):
        if self.has_producer:
            if self.rwlock:
                with self.rwlock.wlock():
                    return eos.push_signed_block(raw_block)
            else:
                return eos.push_signed_block(raw_block)
        else:
            if self.rwlock:
                with self.rwlock.wlock():
                    ret, statistics = self.chain.push_raw_block(raw_block, return_statistics)
                    if statistics:
                        self.logger.info(statistics)
            else:
                ret, statistics = self.chain.push_raw_block(raw_block, return_statistics)
                if statistics:
                    self.logger.info(statistics)


    async def on_signed_block_message(self, raw_msg: bytes):
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

            self.push_block(raw_msg, return_statistics)

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
            self.logger.exception(e)
            if e.json()['stack'][0]['format'].startswith('we already know about this block'):
                self.logger.warning(f"++++++++receive duplicated block: {received_block_num}, block_id: {block_id}")
                return True
            else:
                eos.exit()
                return False
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

    async def handle_sync_request_message(self, message: SyncRequestMessage):
        try:
            for num in range(message.start_block, message.end_block+1):
                raw_block = self.chain.fetch_block_by_number(num)
                if raw_block:
                    if not await self.send_message(SignedBlockMessage(raw_block)):
                        return False
                else:
                    self.logger.info(f"+++++++++no block for num: {num}")
                    break
        except asyncio.exceptions.CancelledError:
            self.logger.info(f"handle_sync_request_message CancelledError")
        self.sync_request_task = None

    async def on_handshake_message(self, message: HandshakeMessage):
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
        elif self.chain.last_irreversible_block_num() > message.head_num + default_block_latency:
            # notice_message note;
            # note.known_trx.pending = chain_info.lib_num;
            # note.known_trx.mode = last_irr_catch_up;
            # note.known_blocks.mode = last_irr_catch_up;
            # note.known_blocks.pending = chain_info.head_num;
            # note.known_blocks.ids.push_back(chain_info.head_id);
            # if (c->protocol_version >= proto_block_range) {
            # // begin, more efficient to encode a block num instead of retrieving actual block id
            # note.known_blocks.ids.push_back(make_block_id(cc.earliest_available_block_num()));
            # }
            known_trx = OrderedIds(IdListModes.last_irr_catch_up, self.chain.last_irreversible_block_num(), [])
            know_blocks = OrderedIds(IdListModes.last_irr_catch_up, self.chain.head_block_num(), [self.chain.head_block_id()])
            msg = NoticeMessage(known_trx, know_blocks)
            self.logger.info(f'send notice message: {msg}')
            return await self.send_message(msg)
        elif self.chain.head_block_num() > message.head_num + default_block_latency:
            ahead_num = self.chain.head_block_num() - message.head_num
            self.logger.info(f"block num is ahead of peer by {ahead_num}")
            # notice_message note;
            # note.known_trx.mode = none;
            # note.known_blocks.mode = catch_up;
            # note.known_blocks.pending = chain_info.head_num;
            # note.known_blocks.ids.push_back(chain_info.head_id);
            # if (c->protocol_version >= proto_block_range) {
            # // begin, more efficient to encode a block num instead of retrieving actual block id
            # note.known_blocks.ids.push_back(make_block_id(cc.earliest_available_block_num()));
            # }
            known_trx = OrderedIds(IdListModes.none, 0, [])
            ids = [self.chain.head_block_id(), utils.make_block_id(self.chain.earliest_available_block_num())]
            know_blocks = OrderedIds(IdListModes.catch_up, self.chain.head_block_num(), ids)
            msg = NoticeMessage(known_trx, know_blocks)
            self.logger.info(f'send notice message: {msg}')
            return await self.send_message(msg)
        return True

    async def on_notice_message(self, message: NoticeMessage):
        if message.known_blocks.mode == IdListModes.catch_up:
            pending = message.known_blocks.pending
            try:
                block_id = message.known_blocks.ids[0]
                # ret = self.chain.fetch_block_by_id(block_id.to_string())
                # self.logger.info(f"++++++++++fetch block by id: {block_id}, ret: {ret}")
            except IndexError:
                msg = GoAwayMessage(GoAwayReason.no_reason, "no blocks in notice message")
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
        return True

    async def on_request_message(self, message: RequestMessage):
        return True

    async def _handle_message(self):
        tp, raw_msg = await self.read_message()
        if not raw_msg or eos.should_exit():
            return False
        if tp == MessageType.handshake.value:
            message = HandshakeMessage.unpack_bytes(raw_msg)
            return await self.on_handshake_message(message)
        elif tp == MessageType.go_away.value:
            message = GoAwayMessage.unpack_bytes(raw_msg)
            self.logger.info(message)
            for listener in self.goway_listeners:
                listener(self, GoAwayMessage.unpack_bytes(raw_msg))
            self.close()
            return False
        elif tp == MessageType.request.value:
            message = RequestMessage.unpack_bytes(raw_msg)
            self.logger.info(message)
            return await self.on_request_message(message)
        elif tp == MessageType.signed_block.value:
            return await self.on_signed_block_message(raw_msg)
        elif tp == MessageType.time.value:
            message = TimeMessage.unpack_bytes(raw_msg)
            # self.logger.info(message)
            await self.handle_time_message(message)
        elif tp == MessageType.sync_request.value:
            message = SyncRequestMessage.unpack_bytes(raw_msg)
            self.logger.info(message)
            if self.sync_request_task:
                self.sync_request_task.cancel()
            self.sync_request_task = asyncio.create_task(self.handle_sync_request_message(message))
            #TODO: create a task to send blocks
        elif tp == MessageType.notice.value:
            message = NoticeMessage.unpack_bytes(raw_msg)
            self.logger.info(f"receive notice message: {message}")
            return await self.on_notice_message(message)
        elif tp == MessageType.packed_transaction.value:
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
