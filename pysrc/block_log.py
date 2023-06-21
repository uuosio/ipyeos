from . import _block_log

class BlockLog(object):
    def __init__(self, block_log_dir: str):
        self.ptr = _block_log.new(block_log_dir)
    
    def get_block_log_ptr(self):
        return _block_log.get_block_log_ptr(self.ptr)

    def read_block_by_num(self, block_num: int):
        return _block_log.read_block_by_num(self.ptr, block_num)

    def read_block_header_by_num(self, block_num: int):
        return _block_log.read_block_header_by_num(self.ptr, block_num)

    def read_block_id_by_num(self, block_num: int):
        return _block_log.read_block_id_by_num(self.ptr, block_num)

    def read_block_by_id(self, block_id: str):
        return _block_log.read_block_by_id(self.ptr, block_id)

    def head(self):
        return _block_log.head(self.ptr)

    def head_id(self):
        return _block_log.head_id(self.ptr)

    def first_block_num(self):
        return _block_log.first_block_num(self.ptr)
