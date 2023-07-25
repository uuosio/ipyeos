import atexit
import copy
import hashlib
import json
import logging
from multiprocessing import Lock
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Union

import yaml
from . import chain, chainapi, database
from . import eos, log, net, node_config
from .database import GeneratedTransactionObjectIndex
from .database_objects import GeneratedTransactionObject
from .packer import Decoder
from .snapshot import Snapshot
from .types import Name
from .trace_api import TraceAPI

logger = log.get_logger(__name__)

log_level_all = 0
log_level_debug = 1
log_level_info = 2
log_level_warn = 3
log_level_error = 4
log_level_off = 5

genesis_state_or_chain_id_version = 3

class DBReadMode(Enum):
    HEAD = 0
    IRREVERSIBLE = 1
    SPECULATIVE = 2

g_chain_config = {
    "sender_bypass_whiteblacklist":[],
    "actor_whitelist":[],
    "actor_blacklist":[],
    "contract_whitelist":[],
    "contract_blacklist":[],
    "action_blacklist":[],
    "key_blacklist":[],
    "blocks_dir":"dd/blocks",
    "state_dir":"dd/state",
    "state_size":104857600,
    "state_guard_size":10485760,
    "sig_cpu_bill_pct":5000,
    "thread_pool_size":2,
    "max_nonprivileged_inline_action_size":4096,
    "read_only":False,
    "force_all_checks":False,
    "disable_replay_opts":False,
    "contracts_console":True,
    "allow_ram_billing_in_notify":False,
    "maximum_variable_signature_length":16384,
    "disable_all_subjective_mitigations":False,
    "terminate_at_block":0,
    "integrity_hash_on_start":False,
    "integrity_hash_on_stop":False,
    "wasm_runtime":"eos_vm_jit",
    "eosvmoc_config":
    {
        "cache_size":1073741824,
        "threads":1
    },
    # oc_auto,
    # oc_all,
    # oc_none
    "eosvmoc_tierup": "oc_none",
    "read_mode": DBReadMode.HEAD.name,
    "block_validation_mode":"FULL",
    "db_map_mode":"mapped",
    "resource_greylist":[],
    "trusted_producers":[],
    "greylist_limit":1000,
    "profile_accounts":[]
}

def contains_genesis_state(version, first_block_num):
    return version < genesis_state_or_chain_id_version or first_block_num == 1

def contains_chain_id(version, first_block_num):
    return version >= genesis_state_or_chain_id_version and first_block_num > 1

def read_genesis_from_block_log(tester):
    with open(f'{tester.data_dir}/blocks/blocks.log', 'rb') as f:
        data = f.read()

    dec = Decoder(data)
    ver = dec.unpack_u32()
    first_block_num = dec.unpack_u32()
    if contains_genesis_state(ver, first_block_num):
        # GenesisState.unpack(dec)
        data = dec.read_bytes(68+8+34)
        chain_id = hashlib.sha256(data).hexdigest()
    elif contains_chain_id(ver, first_block_num):
        chain_id = dec.read_bytes(32).hex()
    assert chain_id == tester.api.get_info()['chain_id']

def read_chain_id_from_block_log(data_dir):
    block_log_file = f'{data_dir}/blocks/blocks.log'
    if not os.path.exists(block_log_file):
        return ''

    with open(block_log_file, 'rb') as f:
        data = f.read(1024)

    dec = Decoder(data)
    ver = dec.unpack_u32()
    first_block_num = dec.unpack_u32()
    if contains_genesis_state(ver, first_block_num):
        # GenesisState.unpack(dec)
        data = dec.read_bytes(68+8+34)
        return hashlib.sha256(data).hexdigest()
    elif contains_chain_id(ver, first_block_num):
        return dec.read_bytes(32).hex()
    assert False, "unknown chain id"

def init(config_file: str, genesis_file: str, snapshot_file: str):
    config = node_config.load_config(config_file)
    logging_config_file = config['logging_config_file']
    chain_config = config['chain']
    state_size=chain_config['state_size']
    data_dir = chain_config['data_dir']
    config_dir = chain_config['config_dir']
    genesis: Optional[Dict] = None

    net_config = config['net']
    peers = net_config['peers']
    logger.info(f'peers: {peers}')
    for peer in peers:
        if peers.count(peer) > 1:
            logger.error(f'duplicated peer: {peer} in config file {config_file}')
            return

    if genesis_file:
        try:
            with open(genesis_file) as f:
                genesis = json.load(f)
        except FileNotFoundError:
            logger.error('genesis file not found: %s', genesis_file)
            return
        except JSONDecodeError:
            logger.error('genesis file is not a valid json file: %s', genesis_file)
            return
        if 'genesis' in config:
            logger.warning(f'genesis in config file {config_file} will be overwrite by genesis file {genesis_file}')
    else:
        try:
            genesis = config['genesis']
        except KeyError:
            pass
    # assert genesis, 'genesis is empty'
    eos.initialize_logging(logging_config_file)

    try:
        debug_producer_key=chain_config['debug_producer_key']
    except KeyError:
        debug_producer_key=''

    return data_dir, config_dir, genesis, state_size, snapshot_file, debug_producer_key

class Node(object):
    def __init__(self, data_dir: str, config_dir: str, genesis: str, state_size: int, snapshot_file: str = '', debug_producer_key: str = '', rwlock = None, worker_process: bool = False):
        self.rwlock = rwlock

        if not worker_process:
            eos.set_data_dir(data_dir)
            eos.set_config_dir(config_dir)

        self._chain = None
        if snapshot_file:
            if not os.path.exists(snapshot_file):
                raise Exception(f'snapshot file {snapshot_file} does not exist')
            if os.path.exists(f'{data_dir}/state/shared_memory.bin'):
                raise Exception(f'{data_dir}/state/shared_memory.bin is already exists while trying to restore the network state from a snapshot')
        atexit.register(self.free)
        self.is_temp_data_dir = True
        self.is_temp_config_dir = True
        self.debug_producer_key=debug_producer_key

        chain_config = copy.copy(g_chain_config)

        if worker_process:
            chain_config['read_only'] = True
            eos.set_worker_process()

        if state_size < 1024*1024*30:
            state_size = 1024*1024*30
        chain_config['state_size'] = state_size

        guard_size = int(state_size * 0.005)
        if guard_size < 1024*1024*5:
            guard_size = 1024*1024*5
        chain_config['state_guard_size'] = guard_size

        if data_dir:
            self.data_dir = data_dir
            self.is_temp_data_dir = False
        else:
            self.data_dir = tempfile.mkdtemp()

        if config_dir:
           self.config_dir = config_dir
           self.is_temp_config_dir = False
        else:
            self.config_dir = tempfile.mkdtemp()

        logger.info('++++data_dir %s', self.data_dir)
        logger.info('++++config_dir %s', self.config_dir)

        chain_config['blocks_dir'] = os.path.join(self.data_dir, 'blocks')
        chain_config['state_dir'] = os.path.join(self.data_dir, 'state')

        try:
            chain_config['db_map_mode'] = node_config.get_chain_config()['db_map_mode']
        except:
            chain_config['db_map_mode'] = 'mapped'

        if snapshot_file:
            initialize = False
            init_database = False
            self.genesis = ''
            self.chain_id = eos.extract_chain_id_from_snapshot(snapshot_file)
        elif os.path.exists(os.path.join(chain_config['state_dir'], 'shared_memory.bin')):
            initialize = False
            init_database = False
            self.genesis = ''
            self.chain_id = read_chain_id_from_block_log(self.data_dir)
        else:
            init_database = True
            self.chain_id = ''

        if genesis:
            if isinstance(genesis, dict):
                self.genesis = json.dumps(genesis)
            else:
                self.genesis = genesis
        else:
            self.genesis = ''

        self.chain_config = chain_config
        self._chain = chain.Chain(json.dumps(chain_config), self.genesis, self.chain_id, os.path.join(self.config_dir, "protocol_features"), snapshot_file, self.debug_producer_key)
        self._chain.startup(init_database)
        self._api = chainapi.ChainApi(self.chain)

        self.db = database.Database(self.chain.get_database())

        try:
            plugins = node_config.get_config()['plugins']

            if 'trace_api' in plugins:
                self.trace = TraceAPI(self.chain, f'{self.data_dir}/traces')
            else:
                self.trace = None

            if 'snapshot' in plugins:
                self.snapshot = Snapshot(self.chain, f'{self.data_dir}/snapshots')
            else:
                self.snapshot = None
        except:
            logger.info('+++++no plugins in config file')

    @property
    def api(self) -> chainapi.ChainApi:
        return self._api

    @property
    def chain(self) -> chain.Chain:
        return self._chain

    def get_trace(self) -> TraceAPI:
        return self.trace

    def get_snapshot(self) -> Snapshot:
        return self.snapshot

    def free(self):
        if not self.chain:
            return
        self.chain.free()
        self._chain = None

        if self.is_temp_data_dir and self.data_dir:
            shutil.rmtree(self.data_dir)
            self.data_dir = None

        if self.is_temp_config_dir and self.config_dir:
            shutil.rmtree(self.config_dir)
            self.config_dir = None

    def __del__(self):
        self.free()

g_network: Optional[net.Network] = None
g_node: Optional[Node] = None

def get_node() -> Node:
    global g_node
    assert g_node, 'node is not started'
    return g_node

def get_network() -> net.Network:
    global g_network
    assert g_network, 'network is not started'
    return g_network

def init_node(config_file: str, genesis_file: str, snapshot_file: str, rwlock = None):
    global g_node

    args = init(config_file, genesis_file, snapshot_file)

    g_node = Node(*args, rwlock)
    return g_node

def init_worker_node(data_dir, config_dir, state_size, rwlock):
    global g_node
    g_node = Node(data_dir, config_dir, '', state_size, '', '', rwlock, True)
    return g_node

async def start_network():
    global g_node
    global g_network
    assert g_node, 'node is not initialized'

    g_network = net.Network(g_node.chain, node_config.get_config()['net']['peers'], g_node.rwlock)
    try:
        await g_network.run()
    except asyncio.exceptions.CancelledError:
        for conn in g_network.connections:
            conn.close()
    g_node.chain.free()
    g_node = None
