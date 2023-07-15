import json
from typing import Dict, List, Union

from .native_modules import _transaction
from . import eos

from .chain_exceptions import get_last_exception
from .packer import Packer
from .types import I64, U8, U16, U32, U64, Checksum256, Name, PrivateKey

class Transaction(object):
    def __init__(self, expiration: U32, ref_block_id: Union[Checksum256, str], max_net_usage_words: U32 = 0, max_cpu_usage_ms: U8 = 0, delay_sec: U32 = 0):
        """
        Initializes a new transaction object with the given parameters.

        Args:
            expiration: The expiration time of the transaction, in seconds since the UNIX epoch.
            ref_block_id: The reference block ID of the transaction.
            max_net_usage_words: The maximum number of words of network bandwidth that the transaction can consume.
            max_cpu_usage_ms: The maximum number of milliseconds of CPU time that the transaction can consume.
            delay_sec: The delay time of the transaction.

        Returns:
            None
        """
        if isinstance(ref_block_id, str):
            ref_block_id = Checksum256.from_string(ref_block_id)
        self.ptr = _transaction.new_transaction(expiration, ref_block_id.to_bytes(), max_net_usage_words, max_cpu_usage_ms, delay_sec)

    def id(self) -> Checksum256:
        """
        Returns the ID of the transaction.

        Args:
            None

        Returns:
            Checksum256: The ID of the transaction.
        """
        raw_id = _transaction.id(self.ptr)
        return Checksum256(raw_id)

    def free(self):
        """
        Frees the memory allocated for the transaction object.

        Args:
            None

        Returns:
            None
        """
        if not self.ptr:
            return

        _transaction.free(self.ptr)
        self.ptr = 0

    def __del__(self):
        self.free()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.free()

    def add_action(self, account: Name, name: Name, data: Union[bytes, Packer], auths: Dict[str, str]):
        """
        Adds an action to the transaction.

        Args:
            account: The name of the account to which the action belongs.
            name: The name of the action.
            data: The packed data for the action.
            auths: A dictionary of authorizations for the action, where the keys are actor names and the values are permission names.

        Returns:
            None
        """
        if isinstance(data, Packer):
            data = data.get_bytes()
        assert isinstance(data, bytes), "data must be bytes or Packer"
        _auths = []
        for actor in auths:
            permission = auths[actor]
            _auths.append((eos.s2n(actor), eos.s2n(permission)))
        _transaction.add_action(self.ptr, eos.s2n(account), eos.s2n(name), data, _auths)

    def sign(self, private_key: PrivateKey, chain_id: Union[Checksum256, str]):
        """
        Signs the transaction with the given private key and chain ID.

        Args:
            private_key (PrivateKey): The private key to sign the transaction with.
            chain_id (Checksum256): The chain ID to sign the transaction with.

        Returns:
            bool: True if the transaction was successfully signed, False otherwise.

        Raises:
            Exception: If an error occurs during the signing process.
        """
        if isinstance(chain_id, str):
            chain_id = Checksum256.from_string(chain_id)

        ret = _transaction.sign(self.ptr, private_key.to_bytes(), chain_id.to_bytes())
        if not ret:
            raise Exception(eos.get_last_error())
        return True

    def pack(self, compress: bool = False) -> bytes:
        """
        Packs the transaction into a binary format that can be sent over the network.

        Args:
            compress: A boolean indicating whether to compress the packed data.

        Returns:
            A bytes object containing the packed transaction data.
        """
        return _transaction.pack(self.ptr, compress)

    @classmethod
    def to_json(cls, data: bytes, result_type: int = 0):
        """
        Convert binary transaction data to a JSON object.

        Args:
            data (bytes): The binary transaction data to convert.
            result_type (int, optional): The type of transaction to return. 
                0 for packed_transaction, 1 for signed_transaction. Defaults to 0.

        Returns:
            dict: A JSON object representing the transaction data.

        """
        ret = _transaction.unpack(data, result_type)
        if not ret:
            raise get_last_exception()
        return json.loads(ret)

