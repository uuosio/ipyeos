from typing import List, Dict

from . import _transaction
from .types import U8, U16, U32, U64, I64, Name, Checksum256, PrivateKey
from . import eos

class Transaction(object):
    def __init__(self, expiration: U32, ref_block_id: Checksum256, max_net_usage_words: U32 = 0, max_cpu_usage_ms: U8 = 0, delay_sec: U32 = 0):
        self.ptr = _transaction.new_transaction(expiration, ref_block_id.to_bytes(), max_net_usage_words, max_cpu_usage_ms, delay_sec)

    def free_transaction(self):
        _transaction.free(self.ptr)

    def add_action(self, account: Name, name: Name, data: bytes, auths: Dict[str, str]):
        _auths = []
        for actor in auths:
            permission = auths[actor]
            _auths.append((eos.s2n(actor), eos.s2n(permission)))
        _transaction.add_action(self.ptr, eos.s2n(account), eos.s2n(name), data, _auths)

    def sign(self, private_key: PrivateKey, chain_id: Checksum256):
        ret = _transaction.sign(self.ptr, private_key.to_bytes(), chain_id.to_bytes())
        if not ret:
            raise Exception(eos.get_last_error())
        return True

    def pack(self, compress: bool = False) -> bytes:
        return _transaction.pack(self.ptr, compress)

    @classmethod
    def unpack(cls, data: bytes, result_type: int = 0):
        """
        result_type: 0 - packed_transaction, 1 - signed_transaction
        """
        return _transaction.unpack(data, result_type)
