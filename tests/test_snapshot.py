import os
import hashlib
import logging
import shutil
import platform

from ipyeos import eos
from ipyeos.tester import chaintester
from ipyeos.tester.chaintester import ChainTester

from ipyeos.extensions.snapshot import Snapshot
from ipyeos.core.chain_exceptions import SnapshotRequestNotFoundException, InvalidSnapshotRequestException

chaintester.chain_config['contracts_console'] = True
dir_name = os.path.dirname(__file__)

logger = logging.getLogger(__name__)

def test_snapshot():
    t = ChainTester(True, data_dir=os.path.join(dir_name, "dd"), config_dir=os.path.join(dir_name, "cd"))
    snapshot_dir = os.path.join(dir_name, 'dd', 'snapshot')
    s = Snapshot(t.chain, snapshot_dir)

    logger.info("+++++++++++head_block_num: %d", t.chain.head_block_num())

    # start_block has already been executed, and on_start_block(head_block_num+1) has been invoke.
    # so, to trigger the snapshot, start_block_num should be at least head_block_num+2
    num = t.chain.head_block_num() + 2
    s.schedule(start_block_num=num, snapshot_description="1")
    # s.schedule(start_block_num = num, end_block_num = num, snapshot_description="1")
    logger.info("++++++++get_requests: %s", s.get_requests())

    t.produce_block()
    t.produce_block()

    num = t.chain.head_block_num() + 2

    try:
        s.schedule(2, 1)
    except InvalidSnapshotRequestException as e:
        logger.error("+++++++++schedule: %s", e)

    schedule_request_id = s.schedule(start_block_num=num, end_block_num=num + 9, block_spacing=3, snapshot_description="1")
    r = s.unschedule(schedule_request_id)
    logger.info("+++++++++unschedule: %s", r)

    try:
        r = s.unschedule(schedule_request_id)
    except SnapshotRequestNotFoundException as e:
        logger.info("+++++++++unschedule: %s", e)

    for i in range(10):
        t.produce_block()
        logger.info("++++++++block_num: %d, get_requests: %s", t.chain.head_block_num(), s.get_requests())
