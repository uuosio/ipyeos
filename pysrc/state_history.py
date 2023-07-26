from . import chain, log
from . import _state_history

from .types import U32, U64, Checksum256
from .chain import Chain
from .chain_exceptions import get_last_exception
from .packer import Packer, Encoder, Decoder

logger = log.get_logger(__name__)

# struct get_status_request_v0 {};

class GetStatusRequestV0(Packer):
    def pack(self, enc):
        return 0

    @classmethod
    def unpack(cls, dec):
        return cls()

    def __repr__(self):
        return f'GetStatusRequestV0()'

    def __str__(self):
        return repr(self)

# struct block_position {
#    uint32_t      block_num = 0;
#    block_id_type block_id  = {};
# };

class BlockPosition(Packer):
    def __init__(self, block_num: U32, block_id: Checksum256):
        self.block_num = block_num
        self.block_id = block_id

    def pack(self, enc):
        pos = enc.pos
        enc.pack_u32(self.block_num)
        enc.pack(self.block_id)
        return enc.pos - pos

    @classmethod
    def unpack(cls, dec):
        block_num = dec.unpack_u32()
        block_id = dec.unpack(Checksum256)
        return cls(block_num, block_id)

    def __repr__(self):
        return f'BlockPosition({self.block_num}, {self.block_id})'

    def __str__(self):
        return repr(self)
    

# struct get_blocks_request_v0 {
#    uint32_t                    start_block_num        = 0;
#    uint32_t                    end_block_num          = 0;
#    uint32_t                    max_messages_in_flight = 0;
#    std::vector<block_position> have_positions         = {};
#    bool                        irreversible_only      = false;
#    bool                        fetch_block            = false;
#    bool                        fetch_traces           = false;
#    bool                        fetch_deltas           = false;
# };

class GetBlocksRequestV0(Packer):
    def __init__(self, start_block_num: U32, end_block_num: U32, max_messages_in_flight: U32, have_positions, irreversible_only, fetch_block, fetch_traces, fetch_deltas):
        self.start_block_num = start_block_num
        self.end_block_num = end_block_num
        self.max_messages_in_flight = max_messages_in_flight
        self.have_positions = have_positions
        self.irreversible_only = irreversible_only
        self.fetch_block = fetch_block
        self.fetch_traces = fetch_traces
        self.fetch_deltas = fetch_deltas

    def pack(self, enc):
        pos = enc.pos
        enc.pack_u32(self.start_block_num)
        enc.pack_u32(self.end_block_num)
        enc.pack_u32(self.max_messages_in_flight)
        enc.pack_list(self.have_positions)
        enc.pack_bool(self.irreversible_only)
        enc.pack_bool(self.fetch_block)
        enc.pack_bool(self.fetch_traces)
        enc.pack_bool(self.fetch_deltas)
        return enc.pos - pos

    @classmethod
    def unpack(cls, dec):
        start_block_num = dec.unpack_u32()
        end_block_num = dec.unpack_u32()
        max_messages_in_flight = dec.unpack_u32()
        have_positions = dec.unpack_list(BlockPosition)
        irreversible_only = dec.unpack_bool()
        fetch_block = dec.unpack_bool()
        fetch_traces = dec.unpack_bool()
        fetch_deltas = dec.unpack_bool()
        return cls(start_block_num, end_block_num, max_messages_in_flight, have_positions, irreversible_only, fetch_block, fetch_traces, fetch_deltas)

    def __repr__(self):
        return f'GetBlocksRequestV0({self.start_block_num}, {self.end_block_num}, {self.max_messages_in_flight}, {self.have_positions}, {self.irreversible_only}, {self.fetch_block}, {self.fetch_traces}, {self.fetch_deltas})'

    def __str__(self):
        return repr(self)

# struct get_blocks_ack_request_v0 {
#    uint32_t num_messages = 0;
# };

class GetBlocksAckRequestV0(Packer):
    def __init__(self, num_messages: U32):
        self.num_messages = num_messages

    def pack(self, enc):
        pos = enc.pos
        enc.pack_u32(self.num_messages)
        return enc.pos - pos

    @classmethod
    def unpack(cls, dec):
        num_messages = dec.unpack_u32()
        return cls(num_messages)

    def __repr__(self):
        return f'GetBlocksAckRequestV0({self.num_messages})'

    def __str__(self):
        return repr(self)

class StateRequest(Packer):
    def __init__(self, value):
        self.value = value

    def pack(self, enc):
        if isinstance(self.value, GetStatusRequestV0):
            tp = 0
        elif isinstance(self.value, GetBlocksRequestV0):
            tp = 1
        elif isinstance(self.value, GetBlocksAckRequestV0):
            tp = 2
        else:
            assert False, f'unknown type: {self.value}'

        pos = enc.pos
        enc.pack_u8(tp)
        enc.pack(self.value)
        return enc.pos - pos
    
    @classmethod
    def unpack(cls, dec):
        if dec.unpack_u8() == 0:
            return cls(dec.unpack(GetStatusRequestV0))
        elif dec.unpack_u8() == 1:
            return cls(dec.unpack(GetBlocksRequestV0))
        elif dec.unpack_u8() == 2:
            return cls(dec.unpack(GetBlocksAckRequestV0))

# struct get_status_result_v0 {
#    block_position head                    = {};
#    block_position last_irreversible       = {};
#    uint32_t       trace_begin_block       = 0;
#    uint32_t       trace_end_block         = 0;
#    uint32_t       chain_state_begin_block = 0;
#    uint32_t       chain_state_end_block   = 0;
#    fc::sha256     chain_id                = {};
# };

class GetStatusResultV0(Packer):
    def __init__(self, head: BlockPosition, last_irreversible: BlockPosition, trace_begin_block: U32, trace_end_block: U32, chain_state_begin_block: U32, chain_state_end_block: U32, chain_id: Checksum256):
        self.head = head
        self.last_irreversible = last_irreversible
        self.trace_begin_block = trace_begin_block
        self.trace_end_block = trace_end_block
        self.chain_state_begin_block = chain_state_begin_block
        self.chain_state_end_block = chain_state_end_block
        self.chain_id = chain_id

    def pack(self, enc):
        pos = enc.pos
        enc.pack(self.head)
        enc.pack(self.last_irreversible)
        enc.pack_u32(self.trace_begin_block)
        enc.pack_u32(self.trace_end_block)
        enc.pack_u32(self.chain_state_begin_block)
        enc.pack_u32(self.chain_state_end_block)
        enc.pack(self.chain_id)
        return enc.pos - pos

    @classmethod
    def unpack(cls, dec):
        head = dec.unpack(BlockPosition)
        last_irreversible = dec.unpack(BlockPosition)
        trace_begin_block = dec.unpack_u32()
        trace_end_block = dec.unpack_u32()
        chain_state_begin_block = dec.unpack_u32()
        chain_state_end_block = dec.unpack_u32()
        chain_id = dec.unpack(Checksum256)
        return cls(head, last_irreversible, trace_begin_block, trace_end_block, chain_state_begin_block, chain_state_end_block, chain_id)

    def __repr__(self):
        return f'GetStatusResultV0({self.head}, {self.last_irreversible}, {self.trace_begin_block}, {self.trace_end_block}, {self.chain_state_begin_block}, {self.chain_state_end_block}, {self.chain_id})'

    def __str__(self):
        return repr(self)

# struct get_blocks_result_base {
#    block_position                head;
#    block_position                last_irreversible;
#    std::optional<block_position> this_block;
#    std::optional<block_position> prev_block;
#    std::optional<bytes>          block;
# };

# struct get_blocks_result_v0 : get_blocks_result_base {
#    std::optional<bytes>          traces;
#    std::optional<bytes>          deltas;
# };

class GetBlocksResultV0(Packer):
    def __init__(self, head: BlockPosition, last_irreversible: BlockPosition, this_block, prev_block, block, traces, deltas):
        self.head = head
        self.last_irreversible = last_irreversible
        self.this_block = this_block
        self.prev_block = prev_block
        self.block = block
        self.traces = traces
        self.deltas = deltas

    def pack(self, enc):
        pos = enc.pos
        enc.pack(self.head)
        enc.pack(self.last_irreversible)
        enc.pack_optional(self.this_block)
        enc.pack_optional(self.prev_block)
        enc.pack(self.block)
        enc.pack(self.traces)
        enc.pack(self.deltas)
        return enc.pos - pos

    @classmethod
    def unpack(cls, dec):
        head = dec.unpack(BlockPosition)
        last_irreversible = dec.unpack(BlockPosition)
        this_block = dec.unpack_optional(BlockPosition)
        prev_block = dec.unpack_optional(BlockPosition)
        block = dec.unpack_optional(bytes)
        traces = dec.unpack_optional(bytes)
        deltas = dec.unpack_optional(bytes)
        return cls(head, last_irreversible, this_block, prev_block, block, traces, deltas)

    def __repr__(self):
        return f'GetBlocksResultV0({self.head}, {self.last_irreversible}, {self.this_block}, {self.prev_block}, {self.block}, {self.traces}, {self.deltas})'

    def __str__(self):
        return repr(self)

class StateHistory(object):

    def __init__(self):
        self.ptr = _state_history.new_state_history()
    
    def initialize(self,
        chain: chain.Chain,
        data_dir: str,
        state_history_dir: str = 'state-history', # state_history
        state_history_retained_dir: str = '', # empty string
        state_history_archive_dir: str = '', # empty string
        state_history_stride = 0, # 0
        max_retained_history_files = 0, # 0
        delete_state_history = False, # false
        trace_history = False, # false
        chain_state_history = False, # false
        state_history_endpoint: str = '127.0.0.1:8080', # 127.0.0.1:8080
        state_history_unix_socket_path: str = '',
        trace_history_debug_mode = False,
        state_history_log_retain_blocks = 0
    ):
        ret = _state_history.initialize(
            self.ptr,
            chain.get_controller(),
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
        if not ret:
            raise get_last_exception()
        return True

    def startup(self):
        if not _state_history.startup(self.ptr):
            raise get_last_exception()
        return True

    def shutdown(self):
        _state_history.shutdown(self.ptr)
