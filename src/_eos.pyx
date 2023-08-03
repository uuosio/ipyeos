# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":
    void eosext_init()

    ctypedef struct eos_cb:
        int init(int argc, char** argv) nogil
        int exec() nogil
        int exec_once() nogil
        void quit() nogil
        void initialize_logging(string& config_path)
        void print_log(int level, string& logger_name, string& message)
        void *post(void *(*fn)(void *), void *args) nogil
        void *get_database()
        void *get_controller()
        void set_log_level(string& logger_name, int level)
        int get_log_level(string& logger_name)
        void enable_deep_mind(void *controller)

        string unpack_native_object(int type, const char *packed_native_object, size_t packed_native_object_size)


        string data_dir()
        string config_dir()

    ctypedef struct database_proxy:
        void set_database(void *db)
        void *get_database()
        int32_t set_data_handler(int32_t (*)(int32_t tp, int64_t id, char *data, size_t size, void* custom_data), void *custom_data)
        int32_t walk(int32_t tp, int32_t index_position)
        int32_t walk_range(int32_t tp, int32_t index_position, char *raw_lower_bound, size_t raw_lower_bound_size, char *raw_upper_bound, size_t raw_upper_bound_size)
        int32_t find(int32_t tp, int32_t index_position, char *raw_data, size_t size, char *out, size_t out_size)

    ctypedef struct ipyeos_proxy:
        string get_last_error()
        void set_last_error(string& error)

        void pack_abi(string& msg, vector[char]& packed_message)

        void pack_native_object(int type, string& msg, vector[char]& packed_message)
        void unpack_native_object(int type, string& packed_message, string& msg)

        uint64_t s2n(string& s)
        string n2s(uint64_t n)

        string get_native_contract(uint64_t contract)

        void enable_native_contracts(bool debug)
        bool is_native_contracts_enabled()

        void enable_debug(bool debug)
        bool is_debug_enabled()

        void set_worker_process(bool worker_process)
        bool is_worker_process()

        string get_chain_config(void *controller)

        string create_key(string& key_type)
        string get_public_key(string &priv_key)
 
        string extract_chain_id_from_snapshot(string& snapshot_dir)

        string sign_digest(string &priv_key, string &digest)

        eos_cb *cb

        bool base58_to_bytes(const string& s, vector[char]& out)
        bool bytes_to_base58(const char* data, size_t data_size, string& out)
        void ripemd160(const char *data, size_t data_size, vector[char]& out)

    ipyeos_proxy *get_ipyeos_proxy() nogil

    void app_quit()

def init_chain():
    eosext_init()

init_chain()

def data_dir():
    return get_ipyeos_proxy().cb.data_dir()

def config_dir():
    return get_ipyeos_proxy().cb.config_dir()

def get_chain_config(uint64_t controller) -> str:
    return get_ipyeos_proxy().get_chain_config(<void *>controller)

def initialize_logging(string& config_path):
    get_ipyeos_proxy().cb.initialize_logging(config_path)

def print_log(int level, string& logger_name, string& message):
    get_ipyeos_proxy().cb.print_log(level, logger_name, message)

def set_log_level(string& logger_name, int level):
    get_ipyeos_proxy().cb.set_log_level(logger_name, level)

def get_log_level(string& logger_name) -> int:
    return get_ipyeos_proxy().cb.get_log_level(logger_name)

def get_last_error():
    ret = get_ipyeos_proxy().get_last_error()
    return ret

def set_last_error(err: str):
    get_ipyeos_proxy().set_last_error(err)

# string unpack_native_object2(int type, const char *packed_native_object, size_t packed_native_object_size)
def unpack_native_object2(int _type, packed_native_object: bytes):
    cdef string result
    result = get_ipyeos_proxy().cb.unpack_native_object(_type, <char *>packed_native_object, len(packed_native_object))
    return result

def pack_abi(string& abi):
    cdef vector[char] packed_abi
    get_ipyeos_proxy().pack_abi(abi, packed_abi)
    return PyBytes_FromStringAndSize(packed_abi.data(), packed_abi.size())

def pack_native_object(int _type, string& msg):
    cdef vector[char] result
    get_ipyeos_proxy().pack_native_object(_type, msg, result)
    return PyBytes_FromStringAndSize(result.data(), result.size())

def unpack_native_object(int _type, string& packed_message):
    cdef string result
    get_ipyeos_proxy().unpack_native_object(_type, packed_message, result)
    return result

def s2n(string& s):
    return get_ipyeos_proxy().s2n(s)

def n2s(uint64_t n):
    return get_ipyeos_proxy().n2s(n)

def enable_debug(bool debug):
    get_ipyeos_proxy().enable_debug(debug)

def is_debug_enabled():
    return get_ipyeos_proxy().is_debug_enabled()

def set_worker_process(bool worker_process):
    get_ipyeos_proxy().set_worker_process(worker_process)

def is_worker_process():
    return get_ipyeos_proxy().is_worker_process()

def create_key(key_type: str):
    return get_ipyeos_proxy().create_key(key_type)

def get_public_key(priv_key: str):
    return get_ipyeos_proxy().get_public_key(priv_key)

def extract_chain_id_from_snapshot(string& snapshot) -> str:
    return get_ipyeos_proxy().extract_chain_id_from_snapshot(snapshot)
 
def sign_digest(digest: str, priv_key) -> str:
    return get_ipyeos_proxy().sign_digest(digest, priv_key)

def init(args):
    cdef int argc;
    cdef char **argv

    argc = len(args)
    argv = <char **>malloc(argc * sizeof(char *))
    for i in range(argc):
        argv[i] = args[i]

    return get_ipyeos_proxy().cb.init(argc, argv)

def run():
    cdef int ret
    with nogil:
        ret = get_ipyeos_proxy().cb.exec()
    return ret

def run_once():
    cdef int ret
    with nogil:
        ret = get_ipyeos_proxy().cb.exec_once()
    return ret

def quit():
    get_ipyeos_proxy().cb.quit()

cdef void *call_python_fn(void* fn_info) noexcept nogil:
    with gil:
        fn, args, kwargs = <object>fn_info
        try:
            ret = fn(*args, **kwargs)
        except Exception as e:
            return <void *><object>e
        return <void *><object>ret

def post(fn, *args, **kwargs):
    cdef void *ret
    fn_info = (fn, args, kwargs)
    with nogil:
        ret = get_ipyeos_proxy().cb.post(call_python_fn, <void *><object>fn_info)
    _ret = <object>ret
    if isinstance(_ret, Exception):
        raise _ret
    return _ret

def get_controller() -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().cb.get_controller()

def get_database() -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().cb.get_database()

def base58_to_bytes(const string& s):
    cdef vector[char] out
    ret = get_ipyeos_proxy().base58_to_bytes(s, out)
    if ret:
        return PyBytes_FromStringAndSize(out.data(), out.size())
    else:
        return None

def bytes_to_base58(data: bytes) -> str:
    cdef string out
    ret = get_ipyeos_proxy().bytes_to_base58(<const char *>data, len(data), out)
    if ret:
        return out
    else:
        return None

# void ripemd160(const char *data, size_t data_size, vector[char]& out)
def ripemd160(data: bytes) -> bytes:
    cdef vector[char] out
    get_ipyeos_proxy().ripemd160(<const char *>data, len(data), out)
    return PyBytes_FromStringAndSize(out.data(), out.size())

def _enable_deep_mind(uint64_t controller):
    get_ipyeos_proxy().cb.enable_deep_mind(<void *>controller)

