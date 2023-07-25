import json
import json as json_
from typing import Dict, List, Optional, Union

from .native_modules import _chain, _chainapi, _eos
from .chain_exceptions import get_last_exception

class ChainApi(object):

    def __init__(self, chain):
        self.ptr = chain.ptr
        self.chain = chain

    def get_info(self, is_json=True):
        ret = _chainapi.get_info(self.ptr)
        return self.parse_return_value(ret, is_json)

    def get_activated_protocol_features(self, lower_bound=0, upper_bound=0xffffffff, limit=10, search_by_block_num=False, reverse=False):
        '''
            struct get_activated_protocol_features_params {
                std::optional<uint32_t>  lower_bound;
                std::optional<uint32_t>  upper_bound;
                uint32_t                 limit = 10;
                bool                     search_by_block_num = false;
                bool                     reverse = false;
            };

            struct get_activated_protocol_features_results {
                fc::variants             activated_protocol_features;
                std::optional<uint32_t>  more;
            };
        '''
        args = json.dumps(
            {
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'limit': limit, 
                'search_by_block_num': search_by_block_num,
                'reverse': reverse
            }
        )
        ret = _chainapi.get_activated_protocol_features(self.ptr, args)
        return self.parse_return_value(ret)

    def get_block(self, block_num_or_id: str):
        '''
            struct get_block_params {
                string block_num_or_id;
            };
        '''
        params = dict(block_num_or_id=block_num_or_id)
        params = json.dumps(params)
        ret = _chainapi.get_block(self.ptr, params)
        return self.parse_return_value(ret)

    def get_block_header_state(self, block_num_or_id: Union[str, int]):
        '''
            struct get_block_header_state_params {
                string block_num_or_id;
            };
        '''
        args = json.dumps(
            {
                'block_num_or_id': str(block_num_or_id)
            }
        )
        ret = _chainapi.get_block_header_state(self.ptr, args)
        return self.parse_return_value(ret)

    def get_account(self, account: str):
        '''
            struct get_account_params {
                name                  account_name;
                std::optional<symbol> expected_core_symbol;
            };
        '''
        args = json.dumps(
            {
                'account_name': account
            }
        )
        ret = _chainapi.get_account(self.ptr, args)
        return self.parse_return_value(ret)

    def get_code(self, account_name: str, code_as_wasm: bool = True):
        '''
            struct get_code_params {
                name account_name;
                bool code_as_wasm = true;
            };

            struct get_code_results {
                name                   account_name;
                string                 wast;
                string                 wasm;
                fc::sha256             code_hash;
                std::optional<abi_def> abi;
            };
        '''
        args = json.dumps(
            {
                'account_name': account_name,
                'code_as_wasm': code_as_wasm 
            }
        )
        ret = _chainapi.get_code(self.ptr, args)
        return self.parse_return_value(ret)

    def get_code_hash(self, account_name: str):
        '''
            struct get_code_hash_results {
                name                   account_name;
                fc::sha256             code_hash;
            };

            struct get_code_hash_params {
                name account_name;
            };
        '''
        args = json.dumps(
            {
                'account_name': account_name
            }            
        )
        ret = _chainapi.get_code_hash(self.ptr, args)
        return self.parse_return_value(ret)

    def get_abi(self, account):
        '''
            struct get_abi_results {
                name                   account_name;
                std::optional<abi_def> abi;
            };

            struct get_abi_params {
                name account_name;
            };
        '''
        params = json.dumps(
            {
                'account_name': account
            }
        )
        ret = _chainapi.get_abi(self.ptr, params)
        return self.parse_return_value(ret)

    def get_raw_code_and_abi(self, account_name: str):
        '''
            struct get_raw_code_and_abi_results {
                name                   account_name;
                chain::blob            wasm;
                chain::blob            abi;
            };

            struct get_raw_code_and_abi_params {
                name                   account_name;
            };
        '''
        params = json.dumps(
            {
                'account_name': account_name
            }
        )
        ret = _chainapi.get_raw_code_and_abi(self.ptr, params)
        return self.parse_return_value(ret)

    def get_raw_abi(self, account_name: str, abi_hash: Optional[str]):
        '''
            struct get_raw_abi_params {
                name                      account_name;
                std::optional<fc::sha256> abi_hash;
            };

            struct get_raw_abi_results {
                name                       account_name;
                fc::sha256                 code_hash;
                fc::sha256                 abi_hash;
                std::optional<chain::blob> abi;
            };
        '''
        if abi_hash:
            params = json.dumps(
                {
                    'account_name': account_name,
                    'abi_hash': abi_hash
                }
            )
        else:
            params = json.dumps(
                {
                    'account_name': account_name
                }
            )
        ret = _chainapi.get_raw_abi(self.ptr, params)
        return self.parse_return_value(ret)

    def get_table_rows(self, json: bool, code: str, scope: str, table: str, lower_bound: str,
                       upper_bound: str, limit: int, key_type='', index_position='', encode_type='dec',
                       reverse = False, show_payer = False, return_json = True):
        '''
            struct get_table_rows_params {
                bool                 json = false;
                name                 code;
                string               scope;
                name                 table;
                string               table_key;
                string               lower_bound;
                string               upper_bound;
                uint32_t             limit = 10;
                string               key_type;  // type of key specified by index_position
                string               index_position; // 1 - primary (first), 2 - secondary index (in order defined by multi_index), 3 - third index, etc
                string               encode_type{"dec"}; //dec, hex , default=dec
                std::optional<bool>  reverse;
                std::optional<bool>  show_payer; // show RAM pyer
                };
        '''
        params = json_.dumps(
            dict(
                json=json,
                code=code,
                scope=scope,
                table=table,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                limit=limit,
                key_type=key_type,
                index_position=index_position,
                encode_type=encode_type,
                reverse=reverse,
                show_payer=show_payer
            )
        )
        ret = _chainapi.get_table_rows(self.ptr, params)
        return self.parse_return_value(ret, return_json)

    def get_table_rows_ex(self, params, return_json = True):
        ret = _chainapi.get_table_rows(self.ptr, params)
        return self.parse_return_value(ret, return_json)

    def get_table_by_scope(self, code: str, table: str, lower_bound: str, upper_bound: str, limit: int, reverse: bool = False):
        '''
            struct get_table_by_scope_params {
                name                 code; // mandatory
                name                 table; // optional, act as filter
                string               lower_bound; // lower bound of scope, optional
                string               upper_bound; // upper bound of scope, optional
                uint32_t             limit = 10;
                std::optional<bool>  reverse;
            };
        '''
        params = json.dumps(
            dict(
                code = code,
                table = table,
                lower_bound = lower_bound,
                upper_bound = upper_bound,
                limit = limit,
                reverse = reverse,
            )
        )
        ret = _chainapi.get_table_by_scope(self.ptr, params)
        return self.parse_return_value(ret)

    def get_currency_balance(self, code: str, account: str, symbol: Optional[str]=''):
        '''
            struct get_currency_balance_params {
                name                  code;
                name                  account;
                std::optional<string> symbol;
            };
        '''
        params = json.dumps(
            dict(
                code=code,
                account=account,
                symbol=symbol
            )
        )
        ret = _chainapi.get_currency_balance(self.ptr, params)
        return self.parse_return_value(ret)

    def get_currency_stats(self, code: str, symbol: str):
        '''
            struct get_currency_stats_params {
                name           code;
                string         symbol;
            };


            struct get_currency_stats_result {
                asset          supply;
                asset          max_supply;
                account_name   issuer;
            };
        '''
        params = json.dumps(
            dict(
                code=code,
                symbol=symbol
            )
        )
        ret = _chainapi.get_currency_stats(self.ptr, params)
        return self.parse_return_value(ret)

    def get_producers(self, _json: bool, lower_bound: str, limit: int):
        '''
            struct get_producers_params {
                bool        json = false;
                string      lower_bound;
                uint32_t    limit = 50;
            };
        '''
        params = dict(
            json=_json,
            lower_bound=lower_bound,
            limit=limit
        )
        params = json.dumps(params)
        ret = _chainapi.get_producers(self.ptr, params)
        ret = self.parse_return_value(ret)
        return ret['rows']

    def get_producer_schedule(self):
        '''
            struct get_producer_schedule_params {
            };

            struct get_producer_schedule_result {
                fc::variant active;
                fc::variant pending;
                fc::variant proposed;
            };
        '''
        ret = _chainapi.get_producer_schedule(self.ptr, "{}")
        return self.parse_return_value(ret)

    def get_scheduled_transactions(self, _json: bool, lower_bound: str, limit: int = 50):
        '''
            struct get_scheduled_transactions_params {
                bool        json = false;
                string      lower_bound;  /// timestamp OR transaction ID
                uint32_t    limit = 50;
            };

            struct get_scheduled_transactions_result {
                fc::variants  transactions;
                string        more; ///< fill lower_bound with this to fetch next set of transactions
            };
        '''
        params = json.dumps(
            dict(
                json=_json,
                lower_bound=lower_bound,
                limit=limit
            )
        )
        ret = _chainapi.get_scheduled_transactions(self.ptr, params)
        return self.parse_return_value(ret)

    def abi_json_to_bin(self, code: str, action: str, args: Dict):
        '''
            struct abi_json_to_bin_params {
                name         code;
                name         action;
                fc::variant  args;
            };
            struct abi_json_to_bin_result {
                vector<char>   binargs;
            };
        '''
        params = json.dumps(
            dict(
                code=code,
                action=action,
                args=args
            )
        )
        ret = _chainapi.abi_json_to_bin(self.ptr, params)
        return self.parse_return_value(ret)

    def abi_bin_to_json(self, code: str, action: str, binargs: str):
        '''
            struct abi_bin_to_json_params {
                name         code;
                name         action;
                vector<char> binargs;
            };
            struct abi_bin_to_json_result {
                fc::variant    args;
            };
        '''
        params = json.dumps(
            dict(
                code=code,
                action=action,
                binargs=binargs
            )
        )
        ret = _chainapi.abi_bin_to_json(self.ptr, params)
        return self.parse_return_value(ret)

    def get_required_keys(self, transaction: Dict, available_keys: List[str]):
        '''
            struct get_required_keys_params {
                fc::variant transaction;
                flat_set<public_key_type> available_keys;
            };
            struct get_required_keys_result {
                flat_set<public_key_type> required_keys;
            };
        '''
        params = dict(
            transaction = transaction,
            available_keys = available_keys,
        )
        params = json.dumps(params)
        ret = _chainapi.get_required_keys(self.ptr, params)
        return self.parse_return_value(ret)

    def get_transaction_id(self, params: dict):
        '''
            using get_transaction_id_params = transaction;
            using get_transaction_id_result = transaction_id_type;
        '''
        ret = _chainapi.get_transaction_id(self.ptr, params)
        return self.parse_return_value(ret)

    def get_kv_table_rows(self, params: dict):
        '''
            struct get_kv_table_rows_params {
                    bool                   json = false;          // true if you want output rows in json format, false as variant
                    name                   code;                  // name of contract
                    name                   table;                 // name of kv table,
                    name                   index_name;            // name of index index
                    string                 encode_type = "bytes"; // "bytes" : binary values in index_value/lower_bound/upper_bound
                    std::optional<string>  index_value;           // index value for point query.  If this is set, it is processed as a point query
                    std::optional<string>  lower_bound;           // lower bound value of index of index_name. If index_value is not set and lower_bound is not set, return from the beginning of range in the prefix
                    std::optional<string>  upper_bound;           // upper bound value of index of index_name, If index_value is not set and upper_bound is not set, It is set to the beginning of the next prefix range.
                    uint32_t               limit = 10;            // max number of rows
                    bool                   reverse = false;       // if true output rows in reverse order
                    bool                   show_payer = false;
            };
        '''
        ret = _chainapi.get_kv_table_rows(self.ptr, params)
        return self.parse_return_value(ret)

    def recover_reversible_blocks(self, old_reversible_blocks_dir: str, new_reversible_blocks_dir: str, reversible_cache_size: int=340*1024*1024, truncate_at_block: int=0):
        ret = _chainapi.recover_reversible_blocks(old_reversible_blocks_dir, new_reversible_blocks_dir, reversible_cache_size, truncate_at_block)
        return self.parse_return_value(ret)

    def repair_log(self, blocks_dir: str, truncate_at_block: int=0):
        ret = _chainapi.repair_log(blocks_dir, truncate_at_block)
        return self.parse_return_value(ret)

    def db_size_api_get(self):
        ret = _chainapi.db_size_api_get(self.ptr)
        return self.parse_return_value(ret)

    def parse_return_value(self, ret, return_json=True):
        success, result = ret
        if not success:
            raise get_last_exception()
        if return_json:
            result = json.loads(result)
        return result

def repair_log(blocks_dir, truncate_at_block: int=0):
    return _chainapi.repair_log(blocks_dir, truncate_at_block)

def recover_reversible_blocks(old_reversible_blocks_dir: str, new_reversible_blocks_dir: str, reversible_cache_size: int=340*1024*1024, truncate_at_block: int=0):
    return _chainapi.recover_reversible_blocks(old_reversible_blocks_dir, new_reversible_blocks_dir, reversible_cache_size, truncate_at_block)
