import os
import asyncio
import secrets
import json
import time

from ipyeos.bases.types import Checksum256, PrivateKey
from ipyeos import eos
from ipyeos.node import net
from ipyeos.bases import log
from ipyeos.tester.chaintester import ChainTester
from ipyeos.core.signed_transaction import SignedTransaction
from ipyeos.core.packed_transaction import PackedTransaction

logger = log.get_logger(__name__)

def test_tx():
    t = ChainTester(False)
    tx = SignedTransaction(int(time.time()), t.chain.head_block_id())
    tx.add_action('eosio.token', 'transfer', b'hello, world', {'eosio': 'active'})
    priv_key = PrivateKey.from_base58('5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3')
    tx.sign(priv_key, Checksum256.empty())
    logger.info(tx.id())
    assert tx.first_authorizer() == 'eosio'

    raw_tx = tx.pack(0)
    logger.info(raw_tx)

    raw_tx = tx.pack(1)
    logger.info(raw_tx)

    logger.info(tx.to_json(0))
    logger.info(tx.to_json(1))

    pt = PackedTransaction.unpack(raw_tx)
    assert pt.first_authorizer() == 'eosio'
    logger.info(pt)
    logger.info(pt.get_signed_transaction())

    pt = PackedTransaction.new_from_signed_transaction(tx, False)
    assert pt.pack() == raw_tx

    try:
        pt = PackedTransaction.unpack(b'aabb')
        assert False
    except Exception as e:
        logger.info(e)
