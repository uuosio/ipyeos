import json
import logging
import os
import tempfile
from datetime import datetime, timedelta

import pytest

from ipyeos import _chain, _eos, eos
from ipyeos.chaintester import ChainTester

eos.set_log_level('default', 0)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s %(lineno)d %(message)s')

logger=logging.getLogger(__name__)

data_dir = tempfile.mkdtemp()
config_dir = tempfile.mkdtemp()

chain_config = {
    'sender_bypass_whiteblacklist': [],
    'actor_whitelist': [],
    'actor_blacklist': [],
    'contract_whitelist': [],
    'contract_blacklist': [],
    'action_blacklist': [],
    'key_blacklist': [],
    'blog': {
      'log_dir': os.path.join(data_dir, 'blocks'),
      'retained_dir': '',
      'archive_dir': 'archive',
      'stride': 4294967295,
      'max_retained_files': 10,
      'fix_irreversible_blocks': True
    },
    'state_dir': os.path.join(data_dir, 'state'),
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
    "max_transaction_net_usage": 524288,
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
    "max_inline_action_size": 524288,
    "max_inline_action_depth": 4,
    "max_authority_depth": 6,
    "max_action_return_value_size": 256,
  }
}



class TestSystem(object):

    @classmethod
    def setup_class(cls):
        cls.tester = ChainTester()

    @classmethod
    def teardown_class(cls):
        cls.tester.free()

    def setup_method(self, method):
        logger.warning('test start: %s', method.__name__)

    def teardown_method(self, method):
        pass

    def test_pack_abi(self):
        abi = '''
{
    "version": "eosio::abi/1.0",
    "types": [],
    "structs": [],
    "actions": [{
        "name": "sayhello",
        "type": "string",
        "ricardian_contract": ""
    }],
    "tables": [],
    "ricardian_clauses": [],
    "error_messages": [],
    "abi_extensions": []
}
'''
        abi = eos.pack_abi(abi)
        logger.info(abi)

    def test_block(self):
        self.tester.produce_block()
        self.tester.push_action('eosio.mpy', 'hellompy', b'')
        self.tester.produce_block()
        num = self.tester.chain.fork_db_head_block_num()
        block = self.tester.chain.fetch_block_by_number(num)
        logger.info(block)
        logger.info(num)
        r = eos.unpack_block(block)
        logger.info(r)

    def test_chain(self):
        _chain_config = json.dumps(chain_config)
        _genesis_test = json.dumps(genesis_test)

        ptr = _chain.chain_new(_chain_config, _genesis_test, os.path.join(config_dir, "protocol_features"), "")
        _chain.chain_say_hello(ptr)
        _chain.startup(ptr, True)

        def isoformat(dt):
            return dt.isoformat(timespec='milliseconds')

        print(os.getpid())

        dt = datetime.now()

        print(_chain.get_block_id_for_num(ptr, 1))
        print(_chain.get_global_properties(ptr))
        print(_chain.get_dynamic_global_properties(ptr))
        print(_chain.fetch_block_by_number(ptr, 1))
        print(_chain.active_producers(ptr))
        print(_chain.fetch_block_state_by_number(ptr, 1))
        print(_chain.get_last_error(ptr))
        print(_chain.is_ram_billing_in_notify_allowed(ptr))

        for i in range(1):
          _chain.abort_block(ptr)
          dt += timedelta(seconds=1)
          _chain.start_block(ptr, isoformat(dt), 0, '')

          print('++++is building block:', _chain.is_building_block(ptr))

          priv_keys = ['5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3']
          priv_keys = json.dumps(priv_keys)
          _chain.finalize_block(ptr, priv_keys)
          print('++++is building block:', _chain.is_building_block(ptr))
          _chain.commit_block(ptr)
          print('++++is building block:', _chain.is_building_block(ptr))

          _chain.chain_free(ptr)


