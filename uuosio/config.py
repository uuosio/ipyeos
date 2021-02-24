import os
import sys
import argparse

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
    "uuos_mainnet": True,
    "genesis_accounts_file": "",
    "wasm_runtime": "wabt",
    "read_mode": "SPECULATIVE",
    "block_validation_mode": "FULL",
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
    def __init__(self, config_file = None):
        self.config_dir = 'cd'
        parser = argparse.ArgumentParser(description='')
        parser.register('type','bool',str2bool) # add type keyword to registries
        parser.add_argument('--data-dir',               type=str, default='dd',                  help='data directory')
        parser.add_argument('--config-dir',             type=str, default='cd',                  help='config directory')
        parser.add_argument('--http-server-address',    type=str, default='127.0.0.1:8888',      help='http server address')

        #p2p
        parser.add_argument('--p2p-listen-endpoint',    type=str, default='127.0.0.1:9876',      help='p2p listen endpoint')
        parser.add_argument('--p2p-peer-address',       type=str, default=[], action='append',   help='p2p peer address')
        parser.add_argument('--network',                type=str, default='test',                help='network: uuos, eos, test')
        parser.add_argument('--max-clients',            type=int, default=25,                    help='Maximum number of clients from which connections are accepted, use 0 for no limit')
        parser.add_argument('--peer-private-key',       type=str, default='[]',                    help='peer private key')
        parser.add_argument('--peer-key',               type=str, default=[], action='append',   help='peer key')
        parser.add_argument('--p2p-max-nodes-per-host',   type=int, default=1,                   help ='Maximum number of client nodes from any single IP address')

        #chain
        parser.add_argument('--hard-replay-blockchain', default=False, action="store_true",      help='clear chain state database, recover as many blocks as possible from the block log, and then replay those blocks')
        parser.add_argument('--replay-blockchain',      default=False, action="store_true",      help='clear chain state database and replay all blocks')
        parser.add_argument('--fix-reversible-blocks',  default=False, action="store_true",      help='recovers reversible block database if that database is in a bad state')
        parser.add_argument('--uuos-mainnet',           type=str2bool, default=True,             help='uuos main network')
        parser.add_argument('--snapshot',               type=str,      default='',               help='File to read Snapshot State from')
        parser.add_argument('--snapshots-dir',          type=str,      default='snapshots',      help='the location of the snapshots directory (absolute path or relative to application data dir)')
        parser.add_argument('--chain-state-db-size-mb', type=int,      default=300,              help='the location of the snapshots directory (absolute path or relative to application data dir)')
        parser.add_argument('--contracts-console',  default=False, action="store_true",      help='')

        #producer
        parser.add_argument('-p', '--producer-name',    type=str, default=[], action='append',   help='ID of producer controlled by this node (e.g. inita; may specify multiple times)')
        parser.add_argument('-e', '--enable-stale-production',    default=False, action="store_true", help='Enable block production, even if the chain is stale.')
        parser.add_argument('--signature-provider',     type=str, default=[], action='append',   help='')

        parser.add_argument('--abi-serializer-max-time-ms',  type=int, default=default_abi_serializer_max_time_ms,         help='Override default maximum ABI serialization time allowed in ms')

        parser.add_argument('--chain-state-db-guard-size-mb',type=int, default=default_state_guard_size//1024//1024,       help="Safely shut down node when free space remaining in the chain state database drops below this size (in MiB).")
        parser.add_argument('--reversible-blocks-db-size-mb', type=int, default=default_reversible_cache_size//1024//1024, help="Maximum size (in MiB) of the reversible blocks database")
        parser.add_argument('--reversible-blocks-db-guard-size-mb', type=int, default=default_reversible_guard_size//1024//1024, help="Safely shut down node when free space remaining in the reverseible blocks database drops below this size (in MiB).")
        parser.add_argument('--plugin', type=str, default=[], action='append', help='')
        # --plugin=eosio::net_api_plugin --plugin=eosio::chain_plugin --plugin=eosio::chain_api_plugin --plugin=eosio::producer_plugin --plugin=eosio::producer_api_plugin
        #--allowed-connection=any
        parser.add_argument('--allowed-connection', type=str, default=[], action='append', help="Can be 'any' or 'producers' or 'specified' or 'none'. If 'specified', peer-key must be specified at least once. If only 'producers', peer-key is not required. 'producers' and 'specified' may be combined.")

        parser.add_argument('-i', '--interact',    default=False, action="store_true", help='Enable interactive console.')
        parser.add_argument('--interact-server',   type=str,  default='', help='Enable interactive console server.')


        #---------history plugin-------
        parser.add_argument('--history-db-size-mb', type=int,  default=300, help='Maximum size (in MiB) of the history database')
        parser.add_argument('--filter-on',          type=str, default=[], action='append', help='')
        parser.add_argument('--filter-out',         type=str, default=[], action='append', help='')
        parser.add_argument('--filter-transfer',    type=str2bool, default=False, action='append', help='')

        parser.add_argument('--wasm-runtime',       type=str,  default='wabt', help='Override default WASM runtime value of wabt/eos_vm/eos_vm_jit/eos_vm_oc')

        parser.add_argument('-l', '--logconf',      type=str,  default='logging.json', help='')

        configs = []
        if not config_file:
            args = sys.argv[1:]
            index = 0
            for arg in args:
                index += 1
                if arg.startswith('--config-dir'):
                    self.config_dir = args[index]
                    break
            config_file = os.path.join(self.config_dir, 'config.ini')

        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                configs = f.readlines()
                configs = self.parse_config(configs)
        configs.extend(sys.argv[1:])

        self._config = parser.parse_args(configs)

        print('++++peer key:', self._config.peer_key)
    #    print(self._config.data_dir, args.config_dir, args.http_server_address, args.p2p_listen_endpoint)
        print(self._config.p2p_peer_address)
        print(self._config.data_dir)
        print(self._config.uuos_mainnet)

        if 'specified' in self._config.allowed_connection:
            if not len(self._config.peer_key):
                raise Exception("At least one peer-key must accompany 'allowed-connection=specified'")

    def get_config(self):
        return self._config

    def parse_config(self, configs):
        line = 0
        args = []
        for config in configs:
            line += 1
            config_bk = config
            i = config.find('#')
            if i >= 0:
                config = config[:i]
            config = config.strip()
            if not config:
                continue
            index = config.find('=')
            if index < 0:
                raise Exception(f'bad config at line {line}: {config_bk}')
            name = config[:index]
            name = name.strip()
            if not name:
                raise Exception(f'bad config at line {line}')
            value = config[index+1:]
            value = value.strip()
            if value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
            config = f'--{name}={value}'
            if name == 'data-dir':
                self.config_dir = value
            args.append(config)
        return args

