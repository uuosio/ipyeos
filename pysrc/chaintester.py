import os
import json
import pytest
import atexit
import logging
import shutil
import tempfile
import subprocess

from ipyeos import chain, chainapi, config
from datetime import datetime, timedelta
from datetime import timezone

from . import log, eos
from typing import List, Dict, Union, Optional
from .types import Name

logger = log.get_logger(__name__)

test_dir = os.path.dirname(__file__)

# default_time = datetime.fromtimestamp(946684800000/1e3, tz=timezone.utc)
default_time = datetime.utcfromtimestamp(946684800000/1e3)

chain_config = {
    'sender_bypass_whiteblacklist': [],
    'actor_whitelist': [],
    'actor_blacklist': [],
    'contract_whitelist': [],
    'contract_blacklist': [],
    'action_blacklist': [],
    'key_blacklist': [],
    'blog': {
      'log_dir': 'dd/blocks',
      'retained_dir': '',
      'archive_dir': 'archive',
      'stride': 4294967295,
      'max_retained_files': 10,
      'fix_irreversible_blocks': True
    },
    'state_dir': 'dd/state',
    'state_size': 2147483648,
    'state_guard_size': 134217728,
    'reversible_cache_size': 356515840,
    'reversible_guard_size': 2097152,
    'sig_cpu_bill_pct': 5000,
    'thread_pool_size': 2,
    'max_retained_block_files': 10,
    'blocks_log_stride': 4294967295,
    'backing_store': 0,
    'persistent_storage_num_threads': 1,
    'persistent_storage_max_num_files': -1,
    'persistent_storage_write_buffer_size': 134217728,
    'persistent_storage_bytes_per_sync': 1048576,
    'persistent_storage_mbytes_batch': 50,
    'abi_serializer_max_time_us': 15000000,
    'max_nonprivileged_inline_action_size': 4096,
    'read_only': False,
    'force_all_checks': False,
    'disable_replay_opts': False,
    'contracts_console': True,
    'allow_ram_billing_in_notify': False,
    'maximum_variable_signature_length': 16384,
    'disable_all_subjective_mitigations': False,
    'terminate_at_block': 0,
    'wasm_runtime': 'eos_vm_jit',
    # 'wasm_runtime': 'eos_vm',
    'eosvmoc_config': {'cache_size': 1073741824, 'threads': 1},
    'eosvmoc_tierup': False,
    'read_mode': 'SPECULATIVE',
    'block_validation_mode': 'FULL',
    'db_map_mode': 'mapped',
    'resource_greylist': [],
    'trusted_producers': [],
    'greylist_limit': 1000
 }

genesis_test = {
  "initial_timestamp": "2019-10-24T00:00:00.888",
  "initial_key": "EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
  "initial_configuration": {
    "max_block_net_usage": 1048576,
    "target_block_net_usage_pct": 1000,
    "max_transaction_net_usage": 642441,
    "base_per_transaction_net_usage": 12,
    "net_usage_leeway": 500,
    "context_free_discount_net_usage_num": 20,
    "context_free_discount_net_usage_den": 100,
    "max_block_cpu_usage": 800000,
    "target_block_cpu_usage_pct": 1000,
    "max_transaction_cpu_usage": 450000,
    "min_transaction_cpu_usage": 100,
    "max_transaction_lifetime": 3600,
    "deferred_trx_expiration_window": 600,
    "max_transaction_delay": 3888000,
    "max_inline_action_size": 4096,
    "max_inline_action_depth": 4,
    "max_authority_depth": 6
  }
}

genesis_test = {
  "initial_timestamp": "2018-06-01T12:00:00.000",
  "initial_key": "EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
  "initial_configuration": {
    "max_block_net_usage": 1048576,
    "target_block_net_usage_pct": 1000,
    "max_transaction_net_usage": 652441,
    "base_per_transaction_net_usage": 12,
    "net_usage_leeway": 500,
    "context_free_discount_net_usage_num": 20,
    "context_free_discount_net_usage_den": 100,
    "max_block_cpu_usage": 960000,
    "target_block_cpu_usage_pct": 1000,
    "max_transaction_cpu_usage": 100000,
    "min_transaction_cpu_usage": 100,
    "max_transaction_lifetime": 3600,
    "deferred_trx_expiration_window": 600,
    "max_transaction_delay": 3888000,
    "max_inline_action_size": 524288,
    "max_inline_action_depth": 4,
    "max_authority_depth": 6,
    "max_action_return_value_size": 256,
  }
}

key_map = {
    'EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV':'5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3',
    'EOS61MgZLN7Frbc2J7giU7JdYjy2TqnfWFjZuLXvpHJoKzWAj7Nst':'5JEcwbckBCdmji5j8ZoMHLEUS8TqQiqBG1DRx1X9DN124GUok9s',
    'EOS5JuNfuZPATy8oPz9KMZV2asKf9m8fb2bSzftvhW55FKQFakzFL':'5JbDP55GXN7MLcNYKCnJtfKi9aD2HvHAdY7g8m67zFTAFkY1uBB',
    'EOS8Znrtgwt8TfpmbVpTKvA2oB8Nqey625CLN8bCN3TEbgx86Dsvr':'5K463ynhZoCDDa4RDcr63cUwWLTnKqmdcoTKTHBjqoKfv4u5V7p',
    'EOS7ent7keWbVgvptfYaMYeF2cenMBiwYKcwEuc11uCbStsFKsrmV':'5KH8vwQkP4QoTwgBtCV5ZYhKmv8mx56WeNrw9AZuhNRXTrPzgYc',
    'EOS8Ep2idd8FkvapNfgUwFCjHBG4EVNAjfUsRRqeghvq9E91tkDaj':'5KT26sGXAywAeUSrQjaRiX9uk9uDGNqC1CSojKByLMp7KRp8Ncw',

    'EOS6AjF6hvF7GSuSd4sCgfPKq5uWaXvGM2aQtEUCwmEHygQaqxBSV':'5JRYimgLBrRLCBAcjHUWCYRv3asNedTYYzVgmiU4q2ZVxMBiJXL',
    'EOS7sPDxfw5yx5SZgQcVb57zS1XeSWLNpQKhaGjjy2qe61BrAQ49o':'5Jbb4wuwz8MAzTB9FJNmrVYGXo4ABb7wqPVoWGcZ6x8V2FwNeDo',
    'EOS89jesRgvvnFVuNtLg4rkFXcBg2Qq26wjzppssdHj2a8PSoWMhx':'5JHRxntHapUryUetZgWdd3cg6BrpZLMJdqhhXnMaZiiT4qdJPhv',
    'EOS73ECcVHVWvuxJVm5ATnqBTCFMtA6WUsdDovdWH5NFHaXNq1hw1':'5Jbh1Dn57DKPUHQ6F6eExX55S2nSFNxZhpZUxNYFjJ1arKGK9Q3',
    'EOS8h8TmXCU7Pzo5XQKqyWwXAqLpPj4DPZCv5Wx9Y4yjRrB6R64ok':'5JJYrXzjt47UjHyo3ud5rVnNEPTCqWvf73yWHtVHtB1gsxtComG',
    'EOS65jj8NPh2EzLwje3YRy4utVAATthteZyhQabpQubxHNJ44mem9':'5J9PozRVudGYf2D4b8JzvGxPBswYbtJioiuvYaiXWDYaihNFGKP',
    'EOS5fVw435RSwW3YYWAX9qz548JFTWuFiBcHT3PGLryWaAMmxgjp1':'5K9AZWR2wEwtZii52vHigrxcSwCzLhhJbNpdXpVFKHP5fgFG5Tx',

    #for manager user accounts
    'EOS7urTYiCkvUz6XAzAr6fMC9NA1hzgzMRbk49MmpDtongEociQUZ':'5J1PLNAFqxw26ryrkGB81erVQyS5gdJ8fSCmcxAmWh9QJ4vKHH5'
}

producer_key_map = {
    'EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV':'5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3',
    'EOS61MgZLN7Frbc2J7giU7JdYjy2TqnfWFjZuLXvpHJoKzWAj7Nst':'5JEcwbckBCdmji5j8ZoMHLEUS8TqQiqBG1DRx1X9DN124GUok9s',
    'EOS5JuNfuZPATy8oPz9KMZV2asKf9m8fb2bSzftvhW55FKQFakzFL':'5JbDP55GXN7MLcNYKCnJtfKi9aD2HvHAdY7g8m67zFTAFkY1uBB',
    'EOS8Znrtgwt8TfpmbVpTKvA2oB8Nqey625CLN8bCN3TEbgx86Dsvr':'5K463ynhZoCDDa4RDcr63cUwWLTnKqmdcoTKTHBjqoKfv4u5V7p',
    'EOS7ent7keWbVgvptfYaMYeF2cenMBiwYKcwEuc11uCbStsFKsrmV':'5KH8vwQkP4QoTwgBtCV5ZYhKmv8mx56WeNrw9AZuhNRXTrPzgYc',
    'EOS8Ep2idd8FkvapNfgUwFCjHBG4EVNAjfUsRRqeghvq9E91tkDaj':'5KT26sGXAywAeUSrQjaRiX9uk9uDGNqC1CSojKByLMp7KRp8Ncw',

    'EOS6AjF6hvF7GSuSd4sCgfPKq5uWaXvGM2aQtEUCwmEHygQaqxBSV':'5JRYimgLBrRLCBAcjHUWCYRv3asNedTYYzVgmiU4q2ZVxMBiJXL',
    'EOS7sPDxfw5yx5SZgQcVb57zS1XeSWLNpQKhaGjjy2qe61BrAQ49o':'5Jbb4wuwz8MAzTB9FJNmrVYGXo4ABb7wqPVoWGcZ6x8V2FwNeDo',
    'EOS89jesRgvvnFVuNtLg4rkFXcBg2Qq26wjzppssdHj2a8PSoWMhx':'5JHRxntHapUryUetZgWdd3cg6BrpZLMJdqhhXnMaZiiT4qdJPhv',
    'EOS73ECcVHVWvuxJVm5ATnqBTCFMtA6WUsdDovdWH5NFHaXNq1hw1':'5Jbh1Dn57DKPUHQ6F6eExX55S2nSFNxZhpZUxNYFjJ1arKGK9Q3',
    'EOS8h8TmXCU7Pzo5XQKqyWwXAqLpPj4DPZCv5Wx9Y4yjRrB6R64ok':'5JJYrXzjt47UjHyo3ud5rVnNEPTCqWvf73yWHtVHtB1gsxtComG',
    'EOS65jj8NPh2EzLwje3YRy4utVAATthteZyhQabpQubxHNJ44mem9':'5J9PozRVudGYf2D4b8JzvGxPBswYbtJioiuvYaiXWDYaihNFGKP',
    'EOS5fVw435RSwW3YYWAX9qz548JFTWuFiBcHT3PGLryWaAMmxgjp1':'5K9AZWR2wEwtZii52vHigrxcSwCzLhhJbNpdXpVFKHP5fgFG5Tx'
}

class ChainTester(object):

    def __init__(self):
        atexit.register(self.free)

        self.data_dir = tempfile.mkdtemp()
        self.config_dir = tempfile.mkdtemp()
        logger.info('++++data_dir %s', self.data_dir)
        logger.info('++++config_dir %s', self.config_dir)

        chain_config['blog']['log_dir'] = os.path.join(self.data_dir, 'blocks')
        chain_config['state_dir'] = os.path.join(self.data_dir, 'state')


        eos.set_log_level('default', 0)
        eos.set_block_interval_ms(1000)

        self.chain_config = json.dumps(chain_config)
        self.genesis_test = json.dumps(genesis_test)
        eos.set_log_level('default', 10)
        self.chain = chain.Chain(self.chain_config, self.genesis_test, os.path.join(self.config_dir, "protocol_features"), "")
        self.chain.startup(True)
        self.api = chainapi.ChainApi(self.chain)

        # logger.info(self.api.get_info())
        # logger.info(self.api.get_account('eosio'))

        self.feature_digests = []
        eos.set_log_level('default', 0)

        self.feature_digests = ['0ec7e080177b2c02b278d5088611686b49d739925a92d9bfcacd7fc6b74053bd']
        self.start_block()

        key = 'EOS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV'
        systemAccounts = [
                'eosio.bpay',
                'eosio.msig',
                'eosio.names',
                'eosio.ram',
                'eosio.ramfee',
                'eosio.saving',
                'eosio.stake',
                'eosio.token',
                'eosio.vpay',
                'eosio.rex',
                'eosio.reserv',
                'eosio.mpy',
#                'uuos',
                'hello',
                'alice',
                'bob',
                'testmetestme',
                'dothetesting',
                'helloworld11'
        ]
        for a in systemAccounts:
            self.create_account('eosio', a, key, key)

        logger.info('+++++++++deploy eosio.token')
        self.deploy_eosio_token()
        logger.info('+++++++++deploy eosio.bios')
        self.deploy_eosio_bios()
        self.produce_block()

        feature_digests = [
            '1a99a59d87e06e09ec5b028a9cbb7749b4a5ad8819004365d02dc4379a8b7241', #'ONLY_LINK_TO_EXISTING_PERMISSION' 
            '2652f5f96006294109b3dd0bbde63693f55324af452b799ee137a81a905eed25', #'FORWARD_SETCODE' 
            '299dcb6af692324b899b39f16d5a530a33062804e41f09dc97e9f156b4476707', #'WTMSIG_BLOCK_SIGNATURES' 
            'ef43112c6543b88db2283a2e077278c315ae2c84719a8b25f25cc88565fbea99', #'REPLACE_DEFERRED' 
            '4a90c00d55454dc5b059055ca213579c6ea856967712a56017487886a4d4cc0f', #'NO_DUPLICATE_DEFERRED_ID' 
            '4e7bf348da00a945489b2a681749eb56f5de00b900014e137ddae39f48f69d67', #'RAM_RESTRICTIONS' 
            '4fca8bd82bbd181e714e283f83e1b45d95ca5af40fb89ad3977b653c448f78c2', #'WEBAUTHN_KEY'
            '5443fcf88330c586bc0e5f3dee10e7f63c76c00249c87fe4fbf7f38c082006b4', #'BLOCKCHAIN_PARAMETERS'
            '68dcaa34c0517d19666e6b33add67351d8c5f69e999ca1e37931bc410a297428', #'DISALLOW_EMPTY_PRODUCER_SCHEDULE'
            '825ee6288fb1373eab1b5187ec2f04f6eacb39cb3a97f356a07c91622dd61d16', #'KV_DATABASE'
            '8ba52fe7a3956c5cd3a656a3174b931d3bb2abb45578befc59f283ecd816a405', #'ONLY_BILL_FIRST_AUTHORIZER'
            'ad9e3d8f650687709fd68f4b90b41f7d825a365b02c23a636cef88ac2ac00c43', #'RESTRICT_ACTION_TO_SELF'
            'bf61537fd21c61a60e542a5d66c3f6a78da0589336868307f94a82bccea84e88', #'CONFIGURABLE_WASM_LIMITS'
            'c3a6138c5061cf291310887c0b5c71fcaffeab90d5deb50d3b9e687cead45071', #'ACTION_RETURN_VALUE'
            'e0fb64b1085cc5538970158d05a009c24e276fb94e1a0bf6a528b48fbc4ff526', #'FIX_LINKAUTH_RESTRICTION'
            'f0af56d2c5a48d60a4a5b5c903edfb7db3a736a94ed589d0b797df33ff9d3e1d', #'GET_SENDER'
        ]
        for digest in feature_digests: 
            try:
                args = {'feature_digest': digest}
                self.push_action('eosio', 'activate', args, {'eosio':'active'})
                self.feature_digests.append(digest)
            except Exception as e:
                logger.info(e)
        self.produce_block()
        logger.info('+++++++++deploy eosio.system')
        self.deploy_eosio_system()
        self.produce_block()

        self.deploy_eosio_msig()

        args = dict(account='eosio.msig', is_priv=1)
        # logger.info('+++++', self.api.get_abi('eosio'))
        self.push_action('eosio', 'setpriv', args, {'eosio':'active'})
        self.produce_block()

        self.main_token = 'EOS'
        args = {"issuer":"eosio", "maximum_supply":f"11000000000.0000 {self.main_token}"}
        r = self.push_action('eosio.token', 'create', args, {'eosio.token':'active'})

        args = {"to":"eosio","quantity":f"1000000000.0000 {self.main_token}", "memo":""}
        r = self.push_action('eosio.token','issue', args, {'eosio':'active'})

        self.transfer('eosio', 'alice', 5000000.0)
        self.transfer('eosio', 'bob', 5000000.0)
        self.transfer('eosio', 'hello', 5000000.0)

        args = dict(version = 0,
                    core = '4,EOS'
        )

        self.push_action('eosio', 'init', args, {'eosio':'active'})

        logger.info('+++++++++deploy micropython')
        self.deploy_micropython()
        self.produce_block()
        # r = self.push_action('eosio.mpy', 'hellompy', b'', {'hello':'active'})
        # logger.info(r['action_traces'][0]['console'])
        # self.buy_ram_bytes('eosio', 'eosio', 10*1024*1024)
        # self.delegatebw('eosio', 'eosio', 1.0, 1.0, transfer=0)

        self.code_cache = {}

    def __enter__(self):
        if not self.chain.is_producing_block():
            self.start_block()

    def __exit__(self, _type, value, traceback):
        self.produce_block()

    def deploy_eosio_token(self):
        code_path = os.path.join(test_dir, 'tests/contracts/eosio.token/eosio.token.wasm')
        abi_path = os.path.join(test_dir, 'tests/contracts/eosio.token/eosio.token.abi')
        with open(code_path, 'rb') as f:
            code = f.read()
        with open(abi_path, 'rb') as f:
            abi = f.read()
        r = self.deploy_contract('eosio.token', code, abi)

    def deploy_eosio_bios(self):
        code_path = os.path.join(test_dir, 'tests/contracts/eosio.bios/eosio.bios.wasm')
        abi_path = os.path.join(test_dir, 'tests/contracts/eosio.bios/eosio.bios.abi')
        with open(code_path, 'rb') as f:
            code = f.read()
        with open(abi_path, 'rb') as f:
            abi = f.read()
        self.deploy_contract('eosio', code, abi)

    def deploy_eosio_system(self):
        code_path = os.path.join(test_dir, 'tests/contracts/eosio.system/eosio.system.wasm')
        # code_path = '/Users/newworld/dev/eosio.contracts/build/contracts/eosio.system/eosio.system.wasm.pp'
        abi_path = os.path.join(test_dir, 'tests/contracts/eosio.system/eosio.system.abi')
        with open(code_path, 'rb') as f:
            code = f.read()
        with open(abi_path, 'rb') as f:
            abi = f.read()
        self.deploy_contract('eosio', code, abi)

    def deploy_eosio_msig(self):
        code_path = os.path.join(test_dir, 'tests/contracts/eosio.msig/eosio.msig.wasm')
        abi_path = os.path.join(test_dir, 'tests/contracts/eosio.msig/eosio.msig.abi')
        with open(code_path, 'rb') as f:
            code = f.read()
        with open(abi_path, 'rb') as f:
            abi = f.read()
        self.deploy_contract('eosio.msig', code, abi)

    def deploy_micropython(self):
        code_path = os.path.join(test_dir, 'tests/contracts/micropython/micropython_eosio.wasm')
        # code_path = '/Users/newworld/dev/uuos3/externals/micropython/build/ports/micropython_eosio.wasm'
        #code_path = '/Users/newworld/dev/uuos3/build/externals/micropython/ports/ipyeos/micropython_eosio.wasm'
        abi_path = os.path.join(test_dir, 'tests/contracts/micropython/micropython.abi')
        with open(code_path, 'rb') as f:
            code = f.read()
        with open(abi_path, 'rb') as f:
            abi = f.read()
        self.deploy_contract('eosio.mpy', code, abi)

    # def start_block(self):
    #     self.chain.start_block(self.calc_pending_block_time(), 0, self.feature_digests)

    def free(self):
        if self.chain:
            self.chain.free()
            self.chain = None

        if self.data_dir:
            shutil.rmtree(self.data_dir)
            shutil.rmtree(self.config_dir)
            self.data_dir = None
            self.config_dir = None

    def __del__(self):
        self.free()

    def get_account(self, account):
        return self.api.get_account(account)

    def find_private_key(self, actor: Name, perm_name: Name):
        result = self.api.get_account(actor)
        keys = []
        for permission in result['permissions']:
            # logger.info("%s %s %s", actor, perm_name, permission)
            if permission['perm_name'] == perm_name:
                for key in permission['required_auth']['keys']:
                    pub_key = key['key']
                    pub_key = pub_key.replace('UUOS', 'EOS', 1)
                    if pub_key in key_map:
                        priv_key = key_map[pub_key]
                        keys.append(priv_key)
        return keys

    def push_action(self, account: Name, action: Name, args: Dict, permissions: Dict={}, explicit_cpu_bill=False):
        auth = []
        for actor in permissions:
            perm = permissions[actor]
            auth.append({'actor': actor, 'permission': perm})
        if not auth:
            auth.append({'actor': account, 'permission': 'active'})

        # logger.debug(f'{account}, {action}, {args}')
        if not isinstance(args, bytes):
            if args:
                args = self.chain.pack_action_args(account, action, args)
                if not args:
                    error = self.chain.get_last_error()
                    raise Exception(f'{error}')
            else:
                args = b''
            # logger.error(f'++++{args}')
        a = {
            'account': account,
            'name': action,
            'data': args.hex(),
            'authorization': auth
        }
        ret = self.push_actions_ex([a], explicit_cpu_bill)
        elapsed = ret['elapsed']
        # if not action == 'activate':
        #     logger.info(f'+++++{account} {action} {elapsed}')
        return ret

    def gen_transaction(self, actions: List, json_str=False):
        _actions = []
        for a in actions:
            _actions.append(self.gen_action(*a))
        return self.gen_transaction_ex(_actions, json_str)

    def gen_transaction_ex(self, actions: List, json_str=False):
        chain_id = self.chain.id()
        ref_block_id = self.chain.last_irreversible_block_id()
        priv_keys = []

        for a in actions:
            if isinstance(a['data'], dict):
                data = self.chain.pack_args(a['account'], a['name'], a['data'])
                a['data'] = data.hex()
        for act in actions:
            for author in act['authorization']:
                keys = self.find_private_key(author['actor'], author['permission'])
                if not keys:
                    actor = author['actor']
                    perm = author['permission']
                    raise Exception(f'private key not found: {actor} {perm}')
                for key in keys:
                    if not key in priv_keys:
                        priv_keys.append(key)
        assert len(priv_keys) >= 1

        priv_keys = json.dumps(priv_keys)
#        priv_key = '5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3'

        actions = json.dumps(actions)
        # expiration = datetime.utcnow() + timedelta(seconds=60*60)

        expiration = self.chain.head_block_time()
        # now = datetime.utcnow()
        # if expiration < now:
        #     expiration = now
        expiration = expiration + timedelta(seconds=60)
        ret = self.chain.gen_transaction(json_str, actions, expiration, ref_block_id, chain_id, False, priv_keys)
        if json_str:
            return json.loads(ret)
        return ret

    def push_actions(self, actions: List, explicit_cpu_bill=False):
        _actions = []
        for a in actions:
            _actions.append(self.gen_action(*a))
        raw_signed_trx = self.gen_transaction_ex(_actions)
        deadline = datetime.max
        billed_cpu_time_us = 100
        result = self.chain.push_transaction(raw_signed_trx, deadline, billed_cpu_time_us, explicit_cpu_bill)
        return result

    def push_actions_ex(self, actions: List, explicit_cpu_bill=False):
        raw_signed_trx = self.gen_transaction_ex(actions)
        deadline = datetime.max
        billed_cpu_time_us = 100
        result = self.chain.push_transaction(raw_signed_trx, deadline, billed_cpu_time_us, explicit_cpu_bill)
        return result

    def calc_pending_block_time(self):
        # base = self.chain.head_block_time()
        # return base + timedelta(microseconds=config.block_interval_us)

#        self.chain.abort_block()
        now = datetime.utcnow()
        base = self.chain.head_block_time()
        if base < now:
            base = now
        min_time_to_next_block = config.block_interval_us - int(base.timestamp()*1e6) % config.block_interval_us
        # print('min_time_to_next_block:', min_time_to_next_block)
        block_time = base + timedelta(microseconds=min_time_to_next_block)
        if block_time - now < timedelta(microseconds=config.block_interval_us/10):
            # block_time += timedelta(microseconds=config.block_interval_us)
            logger.warning("++++block time too small!")
        return block_time

    def start_block(self, block_time=default_time):
        self.chain.abort_block()
        if not block_time:
            self.chain.start_block(self.calc_pending_block_time(), 0, self.feature_digests)
        else:
            # logger.info(block_time)
            self.chain.start_block(block_time, 0, self.feature_digests)

        self.feature_digests.clear()

    def produce_block(self, next_block_time=default_time, start_block=True):
        trxs = self.chain.get_scheduled_transactions()
        deadline = datetime.utcnow() + timedelta(microseconds=10000000)
        priv_keys = []
        for pub_key in self.chain.get_producer_public_keys():
            if pub_key in producer_key_map:
                priv_keys.append(producer_key_map[pub_key])

        for scheduled_tx_id in trxs:
            self.chain.push_scheduled_transaction(scheduled_tx_id, deadline, 100)
        # logger.info("+++priv_keys: %s", priv_keys)
        self.chain.finalize_block(priv_keys)
        self.chain.commit_block()
        if start_block:
            self.start_block(next_block_time)

    def create_account(self, creator: Name, account: Name, owner_key: Name, active_key: Name, ram_bytes: int=0, stake_net: float=0.0, stake_cpu: float=0.0):
        actions = []
        # logger.info(f'{creator} {account}')
        args = {
            'creator': creator,
            'name': account,
            'owner': {'threshold': 1,
                    'keys': [{'key': owner_key, 'weight': 1}],
                    'accounts': [],
                    'waits': []
                    },
            'active': {'threshold': 1,
                        'keys': [{'key': active_key, 'weight': 1}],
                        'accounts': [],
                        'waits': []
                    }
        }
        newaccount_args = self.pack_args('eosio', 'newaccount', args)
        if not newaccount_args:
            raise Exception('bad args')
        newaccount_action = {
            'account': 'eosio',
            'name': 'newaccount',
            'data': newaccount_args.hex(),
            'authorization':[{'actor':creator, 'permission':'active'}]
        }
        actions.append(newaccount_action)

        if ram_bytes:
            args = {'payer':creator, 'receiver':account, 'bytes':ram_bytes}
            act = self.gen_action('eosio', 'buyrambytes', args, {creator:'active'})
            actions.append(act)

        if stake_net or stake_cpu:
            args = {
                'from': creator,
                'receiver': account,
                'stake_net_quantity': '%0.4f %s'%(stake_net, self.main_token),
                'stake_cpu_quantity': '%0.4f %s'%(stake_cpu, self.main_token),
                'transfer': 1
            }
            act = self.gen_action('eosio', 'delegatebw', args, {creator:'active'})
            actions.append(act)

        return self.push_actions_ex(actions)

    def gen_action(self, account, action, args, permissions={}):
        auth = []
        for actor in permissions:
            perm = permissions[actor]
            auth.append({'actor': actor, 'permission': perm})
        if not auth:
            auth.append({'actor': account, 'permission': 'active'})

        if isinstance(args, dict):
            args = self.pack_args(account, action, args)
        assert type(args) is bytes
        return {
            'account': account,
            'name': action,
            'data': args.hex(),
            'authorization': auth
        }


    def buy_ram_bytes(self, payer: Name, receiver: Name, _bytes):
        args = {'payer': payer, 'receiver': receiver, 'bytes': _bytes}
        return self.push_action('eosio', 'buyrambytes', args, {payer:'active'})

    def delegatebw(self, _from: Name, receiver: Name, stake_net: float, stake_cpu: float, transfer: bool=0):
        # logger.info(os.getpid())
        # logger.info(input('<<<'))
        args = {
            'from': _from,
            'receiver': receiver,
            'stake_net_quantity': '%0.4f %s'%(stake_net, self.main_token),
            'stake_cpu_quantity': '%0.4f %s'%(stake_cpu, self.main_token),
            'transfer': transfer
        }
        return self.push_action('eosio', 'delegatebw', args, {_from:'active'})

    def deploy_contract(self, account: Name, code: bytes, abi: str, vm_type: int=0, show_elapse: bool=True):
        actions = []
        setcode = {"account": account,
                   "vmtype": vm_type,
                   "vmversion": 0,
                   "code": code.hex()
        }

        setcode = self.chain.pack_action_args('eosio', 'setcode', setcode)
        setcode = {
            'account': 'eosio',
            'name': 'setcode',
            'data': setcode.hex(),
            'authorization':[{'actor': account, 'permission':'active'}]
        }
        actions.append(setcode)
        if abi:
            abi = eos.pack_abi(abi)
        setabi = self.chain.pack_action_args('eosio', 'setabi', {'account':account, 'abi':abi.hex()})
        setabi = {
            'account': 'eosio',
            'name': 'setabi',
            'data': setabi.hex(),
            'authorization':[{'actor': account, 'permission':'active'}]
        }
        actions.append(setabi)
        # logger.info(actions)
        ret = self.push_actions_ex(actions)
#        logger.info('++++%s', ret)
        elapsed = ret['elapsed']
        # if show_elapse and code:
        #     logger.info(f'+++++deploy contract: {account} {elapsed}')
        # logger.info(ret)
        self.chain.clear_abi_cache(account)
        return ret

    def deploy_code(self, account: Name, code: bytes, vm_type: int=0):
        actions = []
        setcode = {"account": account,
                   "vmtype": vm_type,
                   "vmversion": 0,
                   "code": code.hex()
        }

        setcode = self.chain.pack_action_args('eosio', 'setcode', setcode)
        setcode = {
            'account': 'eosio',
            'name': 'setcode',
            'data': setcode.hex(),
            'authorization':[{'actor': account, 'permission':'active'}]
        }
        actions.append(setcode)
        # logger.info(actions)
        ret = self.push_actions_ex(actions)
#        logger.info('++++%s', ret)
        return ret

    def deploy_abi(self, account: Name, abi: str):
        actions = []
        if abi:
            abi = eos.pack_abi(abi)
        setabi = self.chain.pack_action_args('eosio', 'setabi', {'account':account, 'abi':abi.hex()})
        setabi = {
            'account': 'eosio',
            'name': 'setabi',
            'data': setabi.hex(),
            'authorization':[{'actor': account, 'permission':'active'}]
        }
        actions.append(setabi)
        ret = self.push_actions_ex(actions)
        self.chain.clear_abi_cache(account)
        return ret

    def transfer(self, _from: Name, _to: Name, _amount: float, _memo: str='', token_account: Name='eosio.token', token_name: str='', permission: Name='active'):
        if not token_name:
            token_name = self.main_token
        args = {"from":_from, "to":_to, "quantity":'%.4f %s'%(_amount,token_name), "memo":_memo}
        return self.push_action(token_account, 'transfer', args, {_from:permission})

    def pack_args(self, account: Name, action: Name , args: dict):
        ret = self.chain.pack_action_args(account, action, args)
        if not ret:
            raise Exception('pack error')
        return ret

    def unpack_args(self, account: Name, action: Name, raw_args: bytes):
        ret = self.chain.unpack_action_args(account, action, raw_args)
        if not ret:
            raise Exception('unpack error')
        return ret

    def mp_compile(self, file_name: str, src: str):
        if src in self.code_cache:
            return self.code_cache[src]

        tempdir = tempfile.mkdtemp()
        cur_dir = os.getcwd()
        os.chdir(tempdir)
        try:
            py_file = file_name + '.py'
            with open(py_file, 'w') as f:
                f.write(src)
            mpy_file = os.path.join(tempdir, file_name + '.mpy')
            import mpy_cross
            proc = mpy_cross.run('-o', mpy_file, py_file, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            err = proc.stderr.read()
            if err:
                err = err.decode('utf8')
                raise Exception(err)
            with open(mpy_file, 'rb') as f:
                code = f.read()
                self.code_cache[src] = code
                return code
        except Exception as e:
            raise e
        finally:
            os.chdir(cur_dir)

    def get_balance(self, account):
        params = dict(
            json=True,
            code='eosio.token',
            scope=account,
            table='accounts',
            lower_bound='',
            upper_bound='',
            limit=10,
        )
        try:
            ret = self.api.get_table_rows(params)
            balance = ret['rows'][0]['balance'].split(' ')[0]
            return round(float(balance) * 10000) / 10000
        except Exception as e:
            logger.info(e)
            return 0.0

    def get_table_rows(self, _json, code, scope, table,
                                    lower_bound, upper_bound,
                                    limit,
                                    key_type='',
                                    index_position='', 
                                    reverse = False,
                                    show_payer = False):
        params = dict(
                json=_json,
                code=code,
                scope=scope,
                table=table,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                limit=limit,
                key_type=key_type,
                index_position=index_position,
                reverse = False,
                show_payer = False
        )
        return self.api.get_table_rows(params)

    def s2n(self, s: str) -> int:
        return eos.s2n(s)

    def n2s(self, n: int) -> str:
        return eos.n2s(n)