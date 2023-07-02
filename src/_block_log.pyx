# cython: language_level=3, c_string_type=str, c_string_encoding=utf8

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool
from libc.stdlib cimport malloc
from libc.stdlib cimport free
from cpython.bytes cimport PyBytes_AsStringAndSize, PyBytes_FromStringAndSize

cdef extern from * :
    ctypedef long long int64_t
    ctypedef unsigned long long uint64_t
    ctypedef int int32_t
    ctypedef unsigned int uint32_t
    ctypedef unsigned short uint16_t
    ctypedef unsigned char uint8_t

cdef extern from "_ipyeos.hpp":
    ctypedef struct block_log_proxy:
        void *get_block_log_ptr()
        string read_block_by_num(uint32_t block_num)
        string read_block_header_by_num(uint32_t block_num)
        string read_block_id_by_num(uint32_t block_num)
        string read_block_by_id(const string& id)
        string head()
        uint32_t head_block_num()
        string head_id()
        uint32_t first_block_num()

    ctypedef struct ipyeos_proxy:
        void *new_block_log_proxy(string& block_log_dir)

    ipyeos_proxy *get_ipyeos_proxy() nogil

cdef block_log_proxy *block_log(uint64_t ptr):
    return <block_log_proxy*>ptr

def new(string& block_log_dir) -> uint64_t:
    return <uint64_t>get_ipyeos_proxy().new_block_log_proxy(block_log_dir)

def get_block_log_ptr(uint64_t ptr) -> uint64_t:
    return <uint64_t>block_log(ptr).get_block_log_ptr()

# virtual string read_block_by_num(uint32_t block_num);
def read_block_by_num(uint64_t ptr, uint32_t block_num) -> str:
    return block_log(ptr).read_block_by_num(block_num)

# virtual string read_block_header_by_num(uint32_t block_num);
def read_block_header_by_num(uint64_t ptr, uint32_t block_num) -> str:
    return block_log(ptr).read_block_header_by_num(block_num)

# virtual string read_block_id_by_num(uint32_t block_num);
def read_block_id_by_num(uint64_t ptr, uint32_t block_num) -> str:
    return block_log(ptr).read_block_id_by_num(block_num)

# virtual string read_block_by_id(const string& id);
def read_block_by_id(uint64_t ptr, string& id) -> str:
    return block_log(ptr).read_block_by_id(id)

# virtual string head();
def head(uint64_t ptr) -> str:
    return block_log(ptr).head()

# uint32_t head_block_num()
def head_block_num(uint64_t ptr) -> int:
    return block_log(ptr).head_block_num()

# virtual string head_id();
def head_id(uint64_t ptr) -> str:
    return block_log(ptr).head_id()

# virtual uint32_t first_block_num();
def first_block_num(uint64_t ptr) -> int:
    return block_log(ptr).first_block_num()
