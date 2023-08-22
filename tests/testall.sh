eostest test.py || exit 1
eostest test_rate_limit.py  || exit 1
eostest test_state_history.py  || exit 1
eostest test_block_listener.py  || exit 1
eostest test_read_write_lock.py  || exit 1
eostest test_structs.py  || exit 1
eostest test_block_log.py  || exit 1
eostest test_resource_limit.py  || exit 1
eostest test_sync_block.py  || exit 1
eostest test_database.py  || exit 1
# eostest test_rpc.py  || exit 1
eostest test_transaction.py  || exit 1
eostest test_multi_index.py  || exit 1
eostest test_types.py  || exit 1
# eostest test_net.py  || exit 1
eostest test_utils.py  || exit 1
eostest test_snapshot.py  || exit 1
