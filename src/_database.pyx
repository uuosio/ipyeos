# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":
    ctypedef struct database_proxy:
        uint64_t get_free_memory()
        uint64_t get_total_memory()

        int64_t revision()
        void set_revision(int64_t revision)
        void undo()
        void undo_all()

        void start_undo_session(bool enabled)
        void session_squash()
        void session_undo()
        void session_push()

        int32_t set_data_handler(int32_t (*)(int32_t tp, char *data, size_t size, void* custom_data) noexcept, void *custom_data)
        int32_t walk(int32_t tp, int32_t index_position)
        int32_t walk_range(int32_t tp, int32_t index_position, char *raw_lower_bound, size_t raw_lower_bound_size, char *raw_upper_bound, size_t raw_upper_bound_size)
        int32_t find(int32_t tp, int32_t index_position, char *raw_data, size_t size, vector[char] &out)
        
        int32_t create(int32_t tp, const char *raw_data, size_t raw_data_size)
        int32_t modify(int32_t tp, int32_t index_position, char *raw_key, size_t raw_key_size, char *raw_data, size_t raw_data_size)

        int32_t lower_bound(int32_t tp, int32_t index_position, char *raw_data, size_t size, vector[char] &out)
        int32_t upper_bound(int32_t tp, int32_t index_position, char *raw_data, size_t size, vector[char] &out)

        uint64_t row_count(int32_t tp)

    ctypedef struct ipyeos_proxy:
        void *new_database_proxy(void *db_ptr, bool attach)
        void *new_database(const string& dir, bool read_only, uint64_t shared_file_size, bool allow_dirty)

    ipyeos_proxy *get_ipyeos_proxy() nogil

ctypedef struct python_custom_data:
    void *cb
    void *custom_data

cdef int32_t database_on_data(int32_t tp, char *data, size_t size, void *custom_data) noexcept:
    cdef python_custom_data *_data = <python_custom_data *>custom_data
    _cb = <object>_data.cb
    _custom_dta = <object>_data.custom_data
    return _cb(tp, PyBytes_FromStringAndSize(data, size), _custom_dta)

cdef database_proxy *db(uint64_t ptr):
    return <database_proxy*>ptr

def new_proxy(uint64_t db_ptr, bool attach) -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().new_database_proxy(<void *>db_ptr, attach)

def new_database(const string& state_dir, bool read_only, uint64_t shared_file_size, bool allow_dirty) -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().new_database(state_dir, read_only, shared_file_size, allow_dirty)

# uint64_t get_free_memory(void *_db)
def get_free_memory(uint64_t ptr):
    return db(ptr).get_free_memory()

# uint64_t get_total_memory(void *_db)
def get_total_memory(uint64_t ptr):
    return db(ptr).get_total_memory()

def revision(uint64_t ptr) -> int:
    return db(ptr).revision()

# void set_revision(uint64_t revision)
def set_revision(uint64_t ptr, int64_t revision):
    return db(ptr).set_revision(revision)

def undo(uint64_t ptr):
    return db(ptr).undo()

def undo_all(uint64_t ptr):
    return db(ptr).undo_all()

# void start_undo_session(bool enabled)
def start_undo_session(uint64_t ptr, bool enabled):
    return db(ptr).start_undo_session(enabled)

# void session_squash()
def session_squash(uint64_t ptr):
    return db(ptr).session_squash()

# void session_undo()
def session_undo(uint64_t ptr):
    return db(ptr).session_undo()

# void session_push()
def session_push(uint64_t ptr):
    return db(ptr).session_push()

def create(uint64_t ptr, int32_t tp, raw_data: bytes):
    return db(ptr).create(tp, <const char *>raw_data, len(raw_data))

def modify(uint64_t ptr, int32_t tp, int32_t index_position, raw_key: bytes, raw_data: bytes):
    return db(ptr).modify(tp, index_position, <const char *>raw_key, len(raw_key), <const char *>raw_data, len(raw_data))

def walk(uint64_t ptr, tp: int32_t, index_position: int32_t, cb, custom_data: object):
    cdef python_custom_data data
    data.cb = <void *>cb
    data.custom_data = <void *>custom_data
    db(ptr).set_data_handler(database_on_data, <void *>&data)
    return db(ptr).walk(tp, index_position)

def walk_range(uint64_t ptr, tp: int32_t, index_position: int32_t, raw_lower_bound: bytes, raw_upper_bound: bytes, cb, custom_data: object):
    cdef python_custom_data data

    data.cb = <void *>cb
    data.custom_data = <void *>custom_data
    db(ptr).set_data_handler(database_on_data, <void *>&data)

    ret = db(ptr).walk_range(tp, index_position, <const char *>raw_lower_bound, len(raw_lower_bound), <const char *>raw_upper_bound, len(raw_upper_bound))
    return ret

def find(uint64_t ptr, tp: int32_t, index_position: int32_t, raw_data: bytes):
    cdef vector[char] out

    ret = db(ptr).find(tp, index_position, <const char *>raw_data, len(raw_data), out)
    if ret <= 0:
        return (ret, None)

    raw_data = PyBytes_FromStringAndSize(out.data(), out.size())
    return (ret, raw_data)


def lower_bound(uint64_t ptr, tp: int32_t, index_position: int32_t, raw_data: bytes):
    cdef vector[char] out

    ret = db(ptr).lower_bound(tp, index_position, <const char *>raw_data, len(raw_data), out)
    if ret <= 0:
        return (ret, None)

    raw_data = PyBytes_FromStringAndSize(out.data(), out.size())
    return (ret, raw_data)

def upper_bound(uint64_t ptr, tp: int32_t, index_position: int32_t, raw_data: bytes):
    cdef vector[char] out

    ret = db(ptr).upper_bound(tp, index_position, <const char *>raw_data, len(raw_data), out)
    if ret <= 0:
        return (ret, None)

    raw_data = PyBytes_FromStringAndSize(out.data(), out.size())
    return (ret, raw_data)

def row_count(uint64_t ptr, tp: int32_t):
    return db(ptr).row_count(tp)
