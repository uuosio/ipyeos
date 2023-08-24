import asyncio
import multiprocessing
from typing import Any, Dict, List, Optional, Type, Union

from .messages import GoAwayMessage
from .connection import Connection, OutConnection

from .. import eos
from ..bases import debug, log, utils
from ..core.chain import Chain
from ..bases.types import I16, I64, U16, U32, U64, Checksum256, PublicKey, Signature

genesis_state = 9
abi_def = 10
transaction_type = 11
global_property_type = 12

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
            await asyncio.sleep(0.01)
            seconds -= 0.01
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

        if not connections:
            self.logger.info('+++++++eos on exiting')
            return None

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
                if not self.conn:
                    continue
                self.logger.info('+++++choose fastest connection: %s', self.conn.peer)
                await self.conn.handle_messages()
                await self.sleep(3.0)
            except Exception as e:
                self.logger.exception(e)
                await self.sleep(5.0)

        return False

    async def run(self):
        while not eos.should_exit():
            try:
                ret = await self._run()
                if not ret:
                    break
            except asyncio.exceptions.CancelledError:
                self.logger.info(f"network task CancelledError")
                # self.chain.free()
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
