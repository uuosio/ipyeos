import _chainapi
import json

class ChainApi(object):

    def __init__(self, chain_ptr):
        self.ptr = chain_ptr

    def get_info(self):
        return _chainapi.get_info(self.ptr)

    def get_activated_protocol_features(self, params):
        return _chainapi.get_activated_protocol_features(self.ptr, params)

    def get_block(self, params):
        return _chainapi.get_block(self.ptr, params)

    def get_block_header_state(self, params):
        return _chainapi.get_block_header_state(self.ptr, params)

    def get_account(self, account):
        args = {'account_name': account}
        args = json.dumps(args)
        ret, result = _chainapi.get_account(self.ptr, args)
        if not ret:
            raise Exception(result)
        result = json.loads(result)
        return ret, result

    def get_code(self, params):
        return _chainapi.get_code(self.ptr, params)

    def get_code_hash(self, params):
        return _chainapi.get_code_hash(self.ptr, params)

    def get_abi(self, params):
        return _chainapi.get_abi(self.ptr, params)

    def get_raw_code_and_abi(self, params):
        return _chainapi.get_raw_code_and_abi(self.ptr, params)

    def get_raw_abi(self, params):
        return _chainapi.get_raw_abi(self.ptr, params)

    def get_table_rows(self, params):
        return _chainapi.get_table_rows(self.ptr, params)

    def get_table_by_scope(self, params):
        return _chainapi.get_table_by_scope(self.ptr, params)

    def get_currency_balance(self, params):
    # struct get_currency_balance_params {
    #   name             code;
    #   name             account;
    #   optional<string> symbol;
    # };
        return _chainapi.get_currency_balance(self.ptr, params)

    def get_currency_stats(self, params):
        return _chainapi.get_currency_stats(self.ptr, params)

    def get_producers(self, params):
        return _chainapi.get_producers(self.ptr, params)

    def get_producer_schedule(self, params):
        return _chainapi.get_producer_schedule(self.ptr, params)

    def get_scheduled_transactions(self, params):
        return _chainapi.get_scheduled_transactions(self.ptr, params)

    def abi_json_to_bin(self, params):
        return _chainapi.abi_json_to_bin(self.ptr, params)

    def abi_bin_to_json(self, params):
        return _chainapi.abi_bin_to_json(self.ptr, params)

    def get_required_keys(self, params):
        return _chainapi.get_required_keys(self.ptr, params)

    def get_transaction_id(self, params):
        return _chainapi.get_transaction_id(self.ptr, params)

    def recover_reversible_blocks(self, old_reversible_blocks_dir, new_reversible_blocks_dir, reversible_cache_size = 340*1024*1024, truncate_at_block=0):
        return _chainapi.recover_reversible_blocks(old_reversible_blocks_dir, new_reversible_blocks_dir, reversible_cache_size, truncate_at_block)

    def repair_log(self, blocks_dir, truncate_at_block=0):
        return _chainapi.repair_log(blocks_dir, truncate_at_block)

    def get_table_rows(self, params):
        return _chainapi.get_table_rows(self.ptr, params)

    def db_size_api_get(self):
        return _chainapi.db_size_api_get(self.ptr)

def repair_log(blocks_dir, truncate_at_block=0):
    return _chainapi.repair_log(blocks_dir, truncate_at_block)

def recover_reversible_blocks(old_reversible_blocks_dir, new_reversible_blocks_dir, reversible_cache_size = 340*1024*1024, truncate_at_block=0):
    return _chainapi.recover_reversible_blocks(old_reversible_blocks_dir, new_reversible_blocks_dir, reversible_cache_size, truncate_at_block)
