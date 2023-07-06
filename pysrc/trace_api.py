from .types import I32, U32
from . import _trace_api
from . import _eos

class TraceAPI(object):

    def __init__(self, chain, trace_dir: str, slice_stride: U32 = 1000, minimum_irreversible_history_blocks: I32 = -1, minimum_uncompressed_irreversible_history_blocks: I32 = -1, compression_seek_point_stride: U32 = 6 * 1024 * 1024):
        chain_ptr = chain.get_controller()
        self.ptr = _trace_api.new_trace_api(chain_ptr, trace_dir, slice_stride, minimum_irreversible_history_blocks, minimum_uncompressed_irreversible_history_blocks, compression_seek_point_stride)

    def get_block_trace(self, block_num: U32):
        ret = _trace_api.get_block_trace(self.ptr, block_num)
        if not ret:
            raise Exception(_eos.get_last_error_and_clear())
        return ret