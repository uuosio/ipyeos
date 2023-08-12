# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":
    ctypedef struct key_value_index_proxy:
        bool create(const vector[uint64_t]& key, const vector[uint64_t]& non_unique_key, const vector[char]& value);
        bool modify(const vector[uint64_t]& key, const vector[uint64_t]& non_unique_key, const vector[char]& value);
        bool remove(int key_index, const vector[uint64_t]& key);

        bool find_by_key(int key_index, vector[uint64_t]& key, vector[char]& result);
        bool lower_bound_by_key(int key_index, vector[uint64_t]& key, vector[char]& result);
        bool upper_boundby_key(int key_index, vector[uint64_t]& key, vector[char]& result);


    ctypedef struct u64_double_index_proxy:
        bool create(uint64_t key, double value)
        bool modify(uint64_t key, double old_value, double new_value)
        bool remove(uint64_t key, double old_value)
        bool find(uint64_t first, double second)
        bool lower_bound(uint64_t& first, double& second)
        bool upper_bound(uint64_t& first, double& second)

        bool first(uint64_t& first, double& second);
        bool last(uint64_t& first, double& second);

        bool pop_first(uint64_t& first, double& second);
        bool pop_last(uint64_t& first, double& second);

        uint64_t row_count()

    ctypedef struct ipyeos_proxy:
        u64_double_index_proxy* new_u64_double_index_proxy(int sort_type)
        bool free_u64_double_index_proxy(void *ptr)

    ipyeos_proxy *get_ipyeos_proxy() nogil

def new_u64_double_index(int sort_type) -> uint64_t:
    cdef ipyeos_proxy *proxy = get_ipyeos_proxy()
    cdef u64_double_index_proxy *index = proxy.new_u64_double_index_proxy(sort_type)
    return <uint64_t><void *>index

def free_u64_double_index(uint64_t ptr) -> bool:
    cdef ipyeos_proxy *proxy = get_ipyeos_proxy()
    return proxy.free_u64_double_index_proxy(<void *>ptr)

cdef u64_double_index_proxy *index(uint64_t ptr):
    return <u64_double_index_proxy*>ptr

class u64_double_index:
    def __init__(self, sort_type: int=0):
        self.ptr = new_u64_double_index(sort_type)

    def free(self) -> bool:
        if not self.ptr:
            return False
        ret = free_u64_double_index(self.ptr)
        self.ptr = 0
        return ret

    def __del__(self):
        self.free()
    
    # bool create(uint64_t key, double value)
    def create(self, uint64_t key, double value) -> bool:
        return index(self.ptr).create(key, value)
    # bool modify(uint64_t key, double old_value, double new_value)
    def modify(self, uint64_t key, double old_value, double new_value) -> bool:
        return index(self.ptr).modify(key, old_value, new_value)
    # bool remove(uint64_t key, double old_value)
    def remove(self, uint64_t key, double old_value) -> bool:
        return index(self.ptr).remove(key, old_value)
    # bool find(uint64_t first, double second)
    def find(self, uint64_t first, double second) -> bool:
        return index(self.ptr).find(first, second)
    # bool lower_bound(uint64_t& first, double& second)
    def lower_bound(self, uint64_t first, double second) -> bool:
        ret = index(self.ptr).lower_bound(first, second)
        if not ret:
            return None
        return first, second
    # bool upper_bound(uint64_t& first, double& second)
    def upper_bound(self, uint64_t first, double second) -> bool:
        ret = index(self.ptr).upper_bound(first, second)
        if not ret:
            return None
        return first, second

    # bool first(uint64_t& first, double& second);
    def first(self):
        cdef uint64_t _first = 0
        cdef double _second = 0.0
        ret = index(self.ptr).first(_first, _second)
        if not ret:
            return None
        return (_first, _second)
    # bool last(uint64_t& first, double& second);
    def last(self):
        cdef uint64_t _first = 0
        cdef double _second = 0.0
        ret = index(self.ptr).last(_first, _second)
        if not ret:
            return None
        return (_first, _second)

    # bool pop_first(uint64_t& first, double& second);
    def pop_first(self):
        cdef uint64_t _first = 0
        cdef double _second = 0.0
        ret = index(self.ptr).pop_first(_first, _second)
        if not ret:
            return None
        return (_first, _second)
    # bool pop_last(uint64_t& first, double& second);
    def pop_last(self):
        cdef uint64_t _first = 0
        cdef double _second = 0.0
        ret = index(self.ptr).pop_last(_first, _second)
        if not ret:
            return None
        return (_first, _second)

    # uint64_t row_count()
    def row_count(self) -> uint64_t:
        return index(self.ptr).row_count()
