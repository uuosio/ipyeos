import argparse
import os
import sys
from typing import Optional

import yaml

from . import log

logger = log.get_logger(__name__)

default_abi_serializer_max_time_ms = 15*1000
default_state_guard_size      =    128*1024*1024#
default_reversible_cache_size = 340*1024*1024 # 1MB * 340 blocks based on 21 producer BFT delay
default_reversible_guard_size = 2*1024*1024 # 1MB * 340 blocks based on 21 producer BFT delay

block_interval_ms = 1000
block_interval_us = block_interval_ms*1000

genesis_eos = {
    "initial_timestamp": "2018-06-01T12:00:00.000",
    "initial_key": "EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
    "initial_configuration": {
        "max_block_net_usage": 1048576,
        "target_block_net_usage_pct": 1000,
        "max_transaction_net_usage": 524288,
        "base_per_transaction_net_usage": 12,
        "net_usage_leeway": 500,
        "context_free_discount_net_usage_num": 20,
        "context_free_discount_net_usage_den": 100,
        "max_block_cpu_usage": 200000,
        "target_block_cpu_usage_pct": 1000,
        "max_transaction_cpu_usage": 150000,
        "min_transaction_cpu_usage": 100,
        "max_transaction_lifetime": 3600,
        "deferred_trx_expiration_window": 600,
        "max_transaction_delay": 3888000,
        "max_inline_action_size": 4096,
        "max_inline_action_depth": 4,
        "max_authority_depth": 6
    }
}

default_config = {
    "sender_bypass_whiteblacklist": [],
    "actor_whitelist": [],
    "actor_blacklist": [],
    "contract_whitelist": [],
    "contract_blacklist": [],
    "action_blacklist": [],
    "key_blacklist": [],
    "blocks_dir": "dd/blocks",
    "state_dir": "dd/state",
    "state_size": 1073741824,
    "state_guard_size": 134217728,
    "reversible_cache_size": 356515840,
    "reversible_guard_size": 2097152,
    "sig_cpu_bill_pct": 5000,
    "thread_pool_size": 2,
    "read_only": False,
    "force_all_checks": False,
    "disable_replay_opts": False,
    "contracts_console": False,
    "allow_ram_billing_in_notify": False,
    "disable_all_subjective_mitigations": False,
    "genesis_accounts_file": "",
    "wasm_runtime": "wabt",
    "read_mode": "SPECULATIVE",
    "block_validation_mode": "FULL",
    # enum map_mode {
    #     mapped,
    #     heap,
    #     locked
    # };
    # Database map mode ("mapped", "heap", or "locked").
    # In "mapped" mode database is memory mapped as a file.
    # In "heap" mode database is preloaded in to swappable memory and will use huge pages if available.
    # In "locked" mode database is preloaded, locked in to memory, and will use huge pages if available.
    "db_map_mode": "mapped",
    "db_hugepage_paths": [],
    "resource_greylist": [],
    "trusted_producers": [],
    "greylist_limit": 1000
}

class LogLevel(object):
    all = 0
    debug = 1
    info = 2
    warn = 3
    error = 4
    off  = 5

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

class Config(object):

    def __init__(self, config_file: str):
        with open(config_file) as f:
            self.config = yaml.safe_load(f)
        logger.info(f'config_file: {config_file}, config: {self.config}')

    def get_config(self):
        return self.config

    def get_chain_config(self):
        return self.config['chain']

    def get_net_config(self):
        return self.config['net']
    
    def get_debug_port(self):
        return self.config['debug_port']

config: Optional[Config] = None

def load_config(config_file: str):
    global config
    assert not config
    config = Config(config_file)
    return config.get_config()

def get_config():
    global config
    assert config
    return config.config

def get_chain_config():
    global config
    assert config
    return config.get_chain_config()

def get_net_config():
    global config
    assert config
    return config.get_net_config()
