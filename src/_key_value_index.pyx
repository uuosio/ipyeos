# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from _ipyeos cimport *

cdef extern from "_ipyeos.hpp":
    ctypedef struct key_value_index_proxy:
        bool create(const vector[uint64_t]& key, const vector[uint64_t]& non_unique_key, const vector[char]& value);
        bool modify(const vector[uint64_t]& key, const vector[uint64_t]& non_unique_key, const vector[char]& value);
        bool remove(int key_index, const vector[uint64_t]& key);

        bool find_by_key(int key_index, vector[uint64_t]& key, std::vector[char]& result);
        bool lower_bound_by_key(int key_index, vector[uint64_t]& key, std::vector[char]& result);
        bool upper_boundby_key(int key_index, vector[uint64_t]& key, std::vector[char]& result);

    ctypedef struct ipyeos_proxy:
        void *new_database_proxy(void *db_ptr, bool attach)
        void *new_database(const string& dir, bool read_only, uint64_t shared_file_size, bool allow_dirty)

    ipyeos_proxy *get_ipyeos_proxy() nogil

