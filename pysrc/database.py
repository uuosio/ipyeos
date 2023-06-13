from . import _database
from . import _eos

class Database:
    def __init__(self, db_ptr: int = 0):
        if not db_ptr:
            # default to get db ptr from chain_plugin.chain.db()
            self.db_ptr = _eos.get_database()
        else:
            self.db_ptr = db_ptr
        self.ptr = _database.new()

    def walk(self, tp: int, index_position: int, cb):
        return _database.walk(self.ptr, self.db_ptr, tp, index_position, cb)

    def walk_range(self, tp: int, index_position: int, cb, raw_lower_bound: bytes, raw_upper_bound: bytes):
        return _database.walk_range(self.ptr, self.db_ptr, tp, index_position, cb, raw_lower_bound, raw_upper_bound)

    def find(self, tp: int, index_position: int, raw_key: bytes, max_buffer_size: int = 1024):
        return _database.find(self.ptr, self.db_ptr, tp, index_position, raw_key, max_buffer_size)
