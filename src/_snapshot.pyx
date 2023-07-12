# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":
    ctypedef struct snapshot_proxy:
        uint32_t schedule_snapshot(uint32_t block_spacing, uint32_t start_block_num, uint32_t end_block_num, const string& snapshot_description)
        string unschedule_snapshot(uint32_t sri)
        string get_snapshot_requests()
        void set_db_path(const string& db_path)
        void set_snapshots_path(const string& sn_path)
        void add_pending_snapshot_info(const string& head_block_id, uint32_t head_block_num, int64_t head_block_time, uint32_t version, const string& snapshot_name)

    ctypedef struct ipyeos_proxy:
        void *new_snapshot_proxy(void *chain_ptr)

    ipyeos_proxy *get_ipyeos_proxy() nogil

cdef snapshot_proxy *get_snapshot_proxy(uint64_t snapshot_ptr):
    return <snapshot_proxy *>snapshot_ptr

def new_snapshot(uint64_t chain_ptr):
    return <uint64_t>get_ipyeos_proxy().new_snapshot_proxy(<void *>chain_ptr)

def schedule_snapshot(uint64_t snapshot_ptr, uint32_t block_spacing, uint32_t start_block_num, uint32_t end_block_num, const string& snapshot_description):
    return <uint32_t>get_snapshot_proxy(snapshot_ptr).schedule_snapshot(block_spacing, start_block_num, end_block_num, snapshot_description)

def unschedule_snapshot(uint64_t snapshot_ptr, uint32_t sri):
    return <string>get_snapshot_proxy(snapshot_ptr).unschedule_snapshot(sri)

def get_snapshot_requests(uint64_t snapshot_ptr):
    return <string>get_snapshot_proxy(snapshot_ptr).get_snapshot_requests()

def set_db_path(uint64_t snapshot_ptr, const string& db_path):
    return get_snapshot_proxy(snapshot_ptr).set_db_path(db_path)

def set_snapshots_path(uint64_t snapshot_ptr, const string& sn_path):
    return get_snapshot_proxy(snapshot_ptr).set_snapshots_path(sn_path)

def add_pending_snapshot_info(uint64_t snapshot_ptr, const string& head_block_id, uint32_t head_block_num, int64_t head_block_time, uint32_t version, const string& snapshot_name):
    return get_snapshot_proxy(snapshot_ptr).add_pending_snapshot_info(head_block_id, head_block_num, head_block_time, version, snapshot_name)
