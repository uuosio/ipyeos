import json

from . import _snapshot, eos
from .chain import Chain
from .chain_exceptions import get_last_exception


class Snapshot(object):
    def __init__(self, chain: Chain, snapshot_dir: str):
        self.chain = chain
        self.snapshot_ptr = _snapshot.new_snapshot(chain.get_controller())
        self.set_path(snapshot_dir)
        self.snapshot_dir = snapshot_dir
        self.schedule_request_ids = []

    def schedule(self, start_block_num: int, end_block_num: int = 0, snapshot_description: str='', block_spacing: int = 0):
        if end_block_num == 0:
            end_block_num = start_block_num

        request_id = _snapshot.schedule_snapshot(self.snapshot_ptr, block_spacing, start_block_num, end_block_num, snapshot_description)
        if request_id == 0xffffffff:
            raise get_last_exception()
        self.schedule_request_ids.append(request_id)
        return request_id

    def unschedule(self, sri: int):
        try:
            self.schedule_request_ids.remove(sri)
        except ValueError:
            pass
        ret = _snapshot.unschedule_snapshot(self.snapshot_ptr, sri)
        if not ret:
            raise get_last_exception()
        return json.loads(ret)

    def get_requests(self):
        ret = _snapshot.get_snapshot_requests(self.snapshot_ptr)
        return json.loads(ret)

    def set_path(self, path: str):
        self.set_db_path(path)
        self.set_snapshots_path(path)

    def set_db_path(self, db_path: str):
        return _snapshot.set_db_path(self.snapshot_ptr, db_path)

    def set_snapshots_path(self, sn_path: str):
        return _snapshot.set_snapshots_path(self.snapshot_ptr, sn_path)

    # def add_pending_snapshot_info(self, head_block_id: str, head_block_num: int, head_block_time: int, version: int, snapshot_name: str):
    #     return _snapshot.add_pending_snapshot_info(self.snapshot_ptr, head_block_id, head_block_num, head_block_time, version, snapshot_name)
