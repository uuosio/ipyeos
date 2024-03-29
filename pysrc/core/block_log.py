from .chain_exceptions import get_last_exception
from .signed_block import SignedBlock

from ..native_modules import _block_log, _eos

class BlockLog(object):
    def __init__(self, block_log_dir: str):
        self.ptr = _block_log.new(block_log_dir)
        if not self.ptr:
            raise Exception(_eos.get_last_error())
    
    def get_block_log_ptr(self) -> int:
        return _block_log.get_block_log_ptr(self.ptr)

    def read_block_by_num(self, block_num: int) -> SignedBlock:
        if block_num > self.head_block_num() or block_num < self.first_block_num():
            raise Exception("invalid block number, block_num: %d, head_block_num: %d, first_block_num: %d" % (block_num, self.head_block_num(), self.first_block_num()))
        signed_block_proxy_ptr = _block_log.read_block_by_num(self.ptr, block_num)
        return self.new_signed_block(signed_block_proxy_ptr)

    def read_block_header_by_num(self, block_num: int) -> str:
        if block_num > self.head_block_num() or block_num < self.first_block_num():
            raise Exception("invalid block number, block_num: %d, head_block_num: %d, first_block_num: %d" % (block_num, self.head_block_num(), self.first_block_num()))
        return _block_log.read_block_header_by_num(self.ptr, block_num)

    def read_block_id_by_num(self, block_num: int) -> str:
        if block_num > self.head_block_num() or block_num < self.first_block_num():
            raise Exception("invalid block number, block_num: %d, head_block_num: %d, first_block_num: %d" % (block_num, self.head_block_num(), self.first_block_num()))
        return _block_log.read_block_id_by_num(self.ptr, block_num)

    def read_block_by_id(self, block_id: str) -> str:
        signed_block_proxy_ptr = _block_log.read_block_by_id(self.ptr, block_id)
        return self.new_signed_block(signed_block_proxy_ptr)

    def head(self) -> str:
        signed_block_proxy_ptr = _block_log.head(self.ptr)
        return self.new_signed_block(signed_block_proxy_ptr)

    def head_id(self) -> str:
        return _block_log.head_id(self.ptr)

    def first_block_num(self) -> int:
        return _block_log.first_block_num(self.ptr)

    def head_block_num(self) -> int:
        return _block_log.head_block_num(self.ptr)

    def new_signed_block(self, signed_block_proxy_ptr):
        if not signed_block_proxy_ptr:
            ex = get_last_exception()
            if ex:
                raise ex
            else:
                raise Exception("read head block failed")
        return SignedBlock.init(signed_block_proxy_ptr)
