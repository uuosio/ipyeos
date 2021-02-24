import ujson as json
from datetime import datetime

from uuosio import _chain, _uuos
from uuosio import log
logger = log.get_logger(__name__)

def isoformat(dt):
    return dt.isoformat(timespec='milliseconds')

class Chain(object):

    def __init__(self, config, genesis, protocol_features_dir, snapshot_dir):
        self.new(config, genesis, protocol_features_dir, snapshot_dir)

    def new(self, config, genesis, protocol_features_dir, snapshot_dir):
        """
        Create a new Chain instance
        Code example::
            data = {
                'key': 'value',
            }
            print(data)
        :param dict config: Parameter example
        :param dict genesis: Parameter example
        :param str protocol_features_dir: Parameter example
        :param str snapshot_dir: Parameter example
        :returns str: Return statement
        :raises ValueError: Raises example
        """
        if isinstance(config, dict):
            config = json.dumps(config)
        if isinstance(genesis, dict):
            config = json.dumps(config)
        assert isinstance(config, str)
        assert isinstance(genesis, str)

        self.ptr = _chain.chain_new(config, genesis, protocol_features_dir, snapshot_dir)
        if not self.ptr:
            error = _chain.get_last_error()
            raise Exception(error)

    def startup(self, initdb):
        """
        Startup a chain
        Code example::
            chain.startup(True)
        :param bool initdb
        :returns bool: Return True on success, False on failture.
        """
        return _chain.startup(self.ptr, initdb)

    def free(self):
        """
        Release a chain
        """
        if not self.ptr:
            return
        _chain.chain_free(self.ptr)
        self.ptr = 0

    def id(self):
        """
        Get chain id
        :returns str: Return the chain id
        """
        return _chain.id(self.ptr)

    def start_block(self, _time, confirm_block_count=0, features=None):
        """
        Start a new block
        :param str _time
        :param int confirm_block_count
        :param list features
        """
        if isinstance(_time, datetime):
            _time = _time.isoformat(timespec='milliseconds')
        if features:
            if isinstance(features, list):
                features = json.dumps(features)
        else:
            features = ''
        _chain.start_block(self.ptr, _time, confirm_block_count, features)

    def abort_block(self):
        """
        Abort the current block
        :returns bool
        """
        return _chain.abort_block(self.ptr)

    def get_global_properties(self, json=True):
        '''
        Get global properties
        :returns str
        '''
        ret = _chain.get_global_properties(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def get_dynamic_global_properties(self, json=True):
        ret = _chain.get_dynamic_global_properties(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def get_actor_whitelist(self, json=True):
        ret = _chain.get_actor_whitelist(self.ptr)
        if ret:
            return json.loads(ret)
        return ret

    def get_actor_blacklist(self, json=True):
        ret = _chain.get_actor_blacklist(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def get_contract_whitelist(self, json=True):
        ret = _chain.get_contract_whitelist(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def get_contract_blacklist(self, json=True):
        ret = _chain.get_contract_blacklist(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def get_action_blacklist(self, json=True):
        ret = _chain.get_action_blacklist(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def get_key_blacklist(self, json=True):
        ret = _chain.get_key_blacklist(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def get_key_blacklist(self, json=True):
        ret = _chain.get_key_blacklist(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def set_actor_whitelist(self, whitelist):
        whitelist = json.dumps(whitelist)
        _chain.set_actor_whitelist(self.ptr, whitelist)

    def set_actor_blacklist(self, blacklist):
        blacklist = json.dumps(blacklist)
        _chain.set_actor_blacklist(self.ptr, blacklist)

    def set_contract_whitelist(self, whitelist):
        whitelist = json.dumps(whitelist)
        _chain.set_contract_whitelist(self.ptr, whitelist)

    def set_action_blacklist(self, blacklist):
        blacklist = json.dumps(blacklist)
        _chain.set_action_blacklist(self.ptr, blacklist)

    def set_key_blacklist(self, blacklist):
        blacklist = json.dumps(blacklist)
        _chain.set_key_blacklist(self.ptr, blacklist)

    def head_block_num(self):
        return _chain.head_block_num(self.ptr)

    def head_block_time(self):
        iso_time = _chain.head_block_time(self.ptr)
        return datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%S.%f")

    def head_block_id(self):
        return _chain.head_block_id(self.ptr)

    def head_block_producer(self):
        return _chain.head_block_producer(self.ptr)

    def head_block_header(self, json=True):
        ret = _chain.head_block_header(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def head_block_state(self, json=True):
        ret = _chain.head_block_state(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def fork_db_head_block_num(self):
        return _chain.fork_db_head_block_num(self.ptr)

    def fork_db_head_block_id(self):
        return _chain.fork_db_head_block_id(self.ptr)

    def fork_db_head_block_time(self):
        return _chain.fork_db_head_block_time(self.ptr)

    def fork_db_head_block_producer(self):
        return _chain.fork_db_head_block_producer(self.ptr)

    def fork_db_pending_head_block_num(self):
        return _chain.fork_db_pending_head_block_num(self.ptr)

    def fork_db_pending_head_block_id(self):
        return _chain.fork_db_pending_head_block_id(self.ptr)

    def fork_db_pending_head_block_time(self):
        return _chain.fork_db_pending_head_block_time(self.ptr)

    def fork_db_pending_head_block_producer(self):
        return _chain.fork_db_pending_head_block_producer(self.ptr)

    def pending_block_time(self):
        iso_time = _chain.pending_block_time(self.ptr)
        return datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%S.%f")

    def pending_block_producer(self):
        return _chain.pending_block_producer(self.ptr)

    def pending_block_signing_key(self):
        return _chain.pending_block_signing_key(self.ptr)

    def pending_producer_block_id(self):
        return _chain.pending_producer_block_id(self.ptr)

    def get_pending_trx_receipts(self, json=True):
        ret = _chain.get_pending_trx_receipts(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def active_producers(self, json=True):
        ret = _chain.active_producers(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def pending_producers(self, json=True):
        ret = _chain.pending_producers(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def proposed_producers(self, json=True):
        ret = _chain.proposed_producers(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def last_irreversible_block_num(self):
        return _chain.last_irreversible_block_num(self.ptr)

    def last_irreversible_block_id(self):
        return _chain.last_irreversible_block_id(self.ptr)

    def fetch_block_by_number(self, block_num):
        return _chain.fetch_block_by_number(self.ptr, block_num, raw_block)

    def fetch_block_by_id(self, block_id):
        return _chain.fetch_block_by_id(self.ptr, block_id)

    def fetch_block_state_by_number(self, block_num):
        _chain.fetch_block_state_by_number(self.ptr, block_num)

    def fetch_block_state_by_id(self, block_id):
        return _chain.fetch_block_state_by_id(self.ptr, block_id)

    def get_block_id_for_num(self, block_num):
        return _chain.get_block_id_for_num(self.ptr, block_num)

    def calculate_integrity_hash(self):
        return _chain.calculate_integrity_hash(self.ptr)

    def sender_avoids_whitelist_blacklist_enforcement(self, sender):
        return _chain.sender_avoids_whitelist_blacklist_enforcement(self.ptr, sender)

    def check_actor_list(self, actors):
        return _chain.check_actor_list(self.ptr, actors)

    def check_contract_list(self, code):
        return _chain.check_contract_list(self.ptr, code)

    def check_action_list(self, code, action):
        return _chain.check_action_list(self.ptr, code, action)

    def check_key_list(self, pub_key):
        return _chain.check_key_list(self.ptr, pub_key)

    def is_building_block(self):
        return _chain.is_building_block(self.ptr)

    def is_producing_block(self):
        return _chain.is_producing_block(self.ptr)

    def is_ram_billing_in_notify_allowed(self):
        return _chain.is_ram_billing_in_notify_allowed(self.ptr)

    def add_resource_greylist(self, name):
        _chain.add_resource_greylist(self.ptr, name)

    def remove_resource_greylist(self, name):
        _chain.remove_resource_greylist(self.ptr, name)

    def is_resource_greylisted(self, name):
        return _chain.is_resource_greylisted(self.ptr, name)

    def get_resource_greylist(self):
        return _chain.get_resource_greylist(self.ptr)

    def get_config(self, json=True):
        ret = _chain.get_config(self.ptr)
        if json:
            return json.loads(ret)
        return ret

    def validate_expiration(self, trx):
        return _chain.validate_expiration(self.ptr, trx)

    def validate_tapos(self, trx):
        return _chain.validate_tapos(self.ptr, trx)

    def validate_db_available_size(self):
        return _chain.validate_db_available_size(self.ptr)

    def validate_reversible_available_size(self):
        return _chain.validate_reversible_available_size(self.ptr)

    def is_protocol_feature_activated(self, digest):
        return _chain.is_protocol_feature_activated(self.ptr, digest)

    def is_builtin_activated(self, feature):
        return _chain.is_builtin_activated(self.ptr, feature)

    def is_known_unexpired_transaction(self, trx):
        return _chain.is_known_unexpired_transaction(self.ptr, trx)

    def set_proposed_producers(self, producers):
        return _chain.set_proposed_producers(self.ptr, producers)

    def light_validation_allowed(self, replay_opts_disabled_by_policy):
        return _chain.light_validation_allowed(self.ptr, replay_opts_disabled_by_policy)

    def skip_auth_check(self):
        return _chain.skip_auth_check(self.ptr)

    def skip_db_sessions(self):
        return _chain.skip_db_sessions(self.ptr)

    def skip_trx_checks(self):
        return _chain.skip_trx_checks(self.ptr)

    def contracts_console(self):
        return _chain.contracts_console(self.ptr)

    def is_uuos_mainnet(self):
        return _chain.is_uuos_mainnet(self.ptr)

    def id(self):
        return _chain.id(self.ptr)

    def get_read_mode(self):
        return _chain.get_read_mode(self.ptr)

    def get_validation_mode(self):
        return _chain.get_validation_mode(self.ptr)

    def set_subjective_cpu_leeway(self, leeway):
        _chain.set_subjective_cpu_leeway(self.ptr, leeway)

    def set_greylist_limit(self, limit):
        _chain.set_greylist_limit(self.ptr, limit)

    def get_greylist_limit(self):
        return _chain.get_greylist_limit(self.ptr)

    def add_to_ram_correction(self, account, ram_bytes):
        return _chain.add_to_ram_correction(self.ptr, account, ram_bytes)

    def all_subjective_mitigations_disabled(self):
        return _chain.all_subjective_mitigations_disabled(self.ptr)

    def fork_db_pending_head_block_num(self):
        return _chain.fork_db_pending_head_block_num(self.ptr)

    def get_block_id_for_num(self, num):
        return _chain.get_block_id_for_num(self.ptr, num)

    def fetch_block_by_number(self, block_num):
        return _chain.fetch_block_by_number(self.ptr, block_num)

    def is_building_block(self):
        return _chain.is_building_block(self.ptr)


    def get_unapplied_transactions(self):
        return _chain.get_unapplied_transactions(self.ptr)
 
    def push_transaction(self, packed_trx, deadline, billed_cpu_time_us):
        if isinstance(deadline, datetime):
            deadline = deadline.isoformat(timespec='milliseconds')
        result = _chain.push_transaction(self.ptr, packed_trx, deadline, billed_cpu_time_us)
        if not result:
            result = _chain.get_last_error()
        result = json.loads(result)
        if 'except' in result:
            raise Exception(result)
        return result

    def get_scheduled_transaction(self, sender_id, sender):
        ret = _chain.get_scheduled_transaction(self.ptr, sender_id, sender)
        if ret:
            return json.loads(ret)

    def get_scheduled_transactions(self):
        ret = _chain.get_scheduled_transactions(self.ptr)
        return json.loads(ret)

    def push_scheduled_transaction(self, scheduled_tx_id, deadline, billed_cpu_time_us):
        if isinstance(deadline, datetime):
            deadline = deadline.isoformat(timespec='milliseconds')
        return _chain.push_scheduled_transaction(self.ptr, scheduled_tx_id, deadline, billed_cpu_time_us)

    def commit_block(self):
        return _chain.commit_block(self.ptr)

    def pop_block(self):
        return _chain.pop_block(self.ptr)

    def get_account(self, account):
        return _chain.get_account(self.ptr, account)

    def get_scheduled_producer(self, block_time):
        return _chain.get_scheduled_producer(self.ptr, block_time)

    def get_scheduled_producer(self, block_time):
        if not isinstance(block_time, str):
            block_time = block_time.isoformat(timespec='milliseconds')
        return _chain.get_scheduled_producer(self.ptr, block_time)

    def finalize_block(self, priv_keys):
        if isinstance(priv_keys, list):
            priv_keys = json.dumps(priv_keys)
        _chain.finalize_block(self.ptr, priv_keys)

    def get_producer_public_keys(self):
        ret = _chain.get_producer_public_keys(self.ptr)
        return json.loads(ret)

    def clear_abi_cache(self, account):
        _chain.clear_abi_cache(self.ptr, account)

    def pack_action_args(self, name, action, args):
        if isinstance(args, dict):
            args = json.dumps(args)
        return _chain.pack_action_args(self.ptr, name, action, args)

    def unpack_action_args(self, name, action, raw_args):
        return _chain.unpack_action_args(self.ptr, name, action, raw_args)

    def gen_transaction(self, _actions, expiration, reference_block_id, _id, compress, _private_keys):
        if isinstance(expiration, datetime):
            expiration = isoformat(expiration)
        if isinstance(_actions, dict):
            _actions = json.dumps(_actions)
        return _chain.gen_transaction(self.ptr, _actions, expiration, reference_block_id, _id, compress, _private_keys)

    def get_last_error(self):
        return _chain.get_last_error(self.ptr)

    def set_last_error(self, error):
        _chain.set_last_error(self.ptr, error)

    def get_producer_public_keys(self):
        ret = _chain.get_producer_public_keys(self.ptr)
        logger.info("+++producer_public_keys: %s", ret)
        return json.loads(ret)

