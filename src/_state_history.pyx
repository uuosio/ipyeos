# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":
    ctypedef struct state_history_proxy:
        bool initialize(void *controller,
            string data_dir,
            string state_history_dir, # state_history
            string state_history_retained_dir, # empty string
            string state_history_archive_dir, # empty string
            uint32_t state_history_stride, # 0
            uint32_t max_retained_history_files, # 0
            bool delete_state_history, # false
            bool trace_history, # false
            bool chain_state_history, # false
            string state_history_endpoint, # 127.0.0.1:8080
            string state_history_unix_socket_path,
            bool trace_history_debug_mode,
            uint32_t state_history_log_retain_blocks
        )
        bool startup()
        void shutdown()

    ctypedef struct eos_cb:
        state_history_proxy *new_state_history_proxy()

    ctypedef struct ipyeos_proxy:
        eos_cb *cb

    ipyeos_proxy *get_ipyeos_proxy() nogil

cdef state_history_proxy *proxy(uint64_t ptr):
    return <state_history_proxy *>ptr

def new_state_history():
    return <uint64_t>get_ipyeos_proxy().cb.new_state_history_proxy()

def initialize(uint64_t ptr, uint64_t controller,
    const string& data_dir,
    const string& state_history_dir, # state_history
    const string& state_history_retained_dir, # empty string
    const string& state_history_archive_dir, # empty string
    uint32_t state_history_stride, # 0
    uint32_t max_retained_history_files, # 0
    bool delete_state_history, # false
    bool trace_history, # false
    bool chain_state_history, # false
    const string& state_history_endpoint, # 127.0.0.1:8080
    const string& state_history_unix_socket_path,
    bool trace_history_debug_mode,
    uint32_t state_history_log_retain_blocks
):
    return proxy(ptr).initialize(
        <void *>controller,
        data_dir,
        state_history_dir,
        state_history_retained_dir,
        state_history_archive_dir,
        state_history_stride,
        max_retained_history_files,
        delete_state_history,
        trace_history,
        chain_state_history,
        state_history_endpoint,
        state_history_unix_socket_path,
        trace_history_debug_mode,
        state_history_log_retain_blocks
    )

def startup(uint64_t ptr):
    return proxy(ptr).startup()

def shutdown(uint64_t ptr):
    proxy(ptr).shutdown()
