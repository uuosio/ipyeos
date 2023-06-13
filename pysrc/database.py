from . import _database
from . import _eos

null_object_type = 0
account_object_type = 1
account_metadata_object_type = 2
permission_object_type = 3
permission_usage_object_type = 4
permission_link_object_type = 5
# UNUSED_action_code_object_type,
key_value_object_type = 7
index64_object_type = 8
index128_object_type = 9
index256_object_type = 10
index_double_object_type = 11
index_long_double_object_type = 12
global_property_object_type = 13
dynamic_global_property_object_type = 14
block_summary_object_type = 15
transaction_object_type = 16
generated_transaction_object_type = 17
# UNUSED_producer_object_type = 18
# UNUSED_chain_property_object_type = 19
# account_control_history_object_type = 20 #     ///< Defined by history_plugin
# UNUSED_account_transaction_history_object_type = 21
# UNUSED_transaction_history_object_type = 22
# public_key_history_object_type = 23          ///< Defined by history_plugin
# UNUSED_balance_object_type = 24
# UNUSED_staked_balance_object_type = 25
# UNUSED_producer_votes_object_type = 26
# UNUSED_producer_schedule_object_type = 27
# UNUSED_proxy_vote_object_type = 28
# UNUSED_scope_sequence_object_type = 29
table_id_object_type = 30
resource_limits_object_type = 31
resource_usage_object_type = 32
resource_limits_state_object_type = 33
resource_limits_config_object_type = 34
# UNUSED_account_history_object_type = 35 #              ///< Defined by history_plugin
# UNUSED_action_history_object_type = 36 #               ///< Defined by history_plugin
# UNUSED_reversible_block_object_type = 37
protocol_state_object_type = 38
account_ram_correction_object_type = 39
code_object_type = 40
database_header_object_type = 41
      
class Database:
    def __init__(self, db_ptr: int = 0):
        if not db_ptr:
            # default to get db ptr from chain_plugin.chain.db()
            self.db_ptr = _eos.get_database()
        else:
            self.db_ptr = db_ptr
        self.ptr = _database.new()

    def walk(self, tp: int, index_position: int, cb):
        ret = _database.walk(self.ptr, self.db_ptr, tp, index_position, cb)
        if ret == -2:
            raise Exception(_eos.get_last_error())
        return ret

    def walk_range(self, tp: int, index_position: int, cb, raw_lower_bound: bytes, raw_upper_bound: bytes):
        ret = _database.walk_range(self.ptr, self.db_ptr, tp, index_position, cb, raw_lower_bound, raw_upper_bound)
        if ret == -2:
            raise Exception(_eos.get_last_error())
        return ret

    def find(self, tp: int, index_position: int, raw_key: bytes, max_buffer_size: int = 1024):
        ret, raw_data = _database.find(self.ptr, self.db_ptr, tp, index_position, raw_key, max_buffer_size)
        if ret == -2:
            raise Exception(_eos.get_last_error())
        return ret, raw_data
