import os
import logging
import time

from ipyeos.chaintester import ChainTester
from ipyeos.block_log import BlockLog
from ipyeos.trace_api import TraceAPI

logger = logging.getLogger(__name__)

def test_sync():
    state_size = 32*1024*1024*1024
    data_name = './data'

    snapshot_dir = ''
    t = ChainTester(True, data_dir="dd", config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_file='')
    t.chain.abort_block()

    trace = TraceAPI(t.chain, f'{t.data_dir}/trace')
    num = t.chain.head_block_num()

    info = trace.get_block_trace(num + 1)
    logger.info(info)

    info = t.api.get_info()
    head_block_num = info['head_block_num']
    blog = BlockLog('dd/blocks')
    logger.info("%s %s", head_block_num, blog.head_block_num())
    num_count = blog.head_block_num() - head_block_num

    start = time.monotonic()
    count_start_time = start
    total_count = 0
    count = 0
    for block_num in range(head_block_num+1, head_block_num+num_count+1):
        total_count += 1
        count += 1
        duration = time.monotonic() - start
        if duration >= 30.0:
            total_time = time.monotonic() - count_start_time
            remaining_blocks = num_count - total_count
            logger.info(f"++++++push block speed: {round(total_count/duration, 1)} b/s, remaining time: {round(total_time/total_count*remaining_blocks/60, 1)} minutes, remaining blocks: {remaining_blocks}")
            start = time.monotonic()
            count = 0
        t.chain.push_block(blog, block_num)


def test_2sync():
    state_size = 32*1024*1024*1024
    data_name = './data'

    snapshot_dir = ''
    t = ChainTester(True, data_dir="dd", config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_file='')
    t.chain.abort_block()

    trace = TraceAPI(t.chain, f'{t.data_dir}/trace')
    head_block_num = t.chain.head_block_num()

    blog = BlockLog('dd/blocks')
    t.chain.push_block(blog, head_block_num + 1)

    info = trace.get_block_trace(head_block_num + 1)
    logger.info(info)


def test_3sync():
    state_size = 32*1024*1024*1024
    data_name = './data'

    snapshot_dir = ''
    t = ChainTester(True, data_dir="dd", config_dir='cd', state_size=state_size, snapshot_file='')
    t.chain.abort_block()

    trace = TraceAPI(t.chain, f'{t.data_dir}/trace')
    head_block_num = t.chain.head_block_num()

    info = trace.get_block_trace(head_block_num + 1)
    logger.info(info)
