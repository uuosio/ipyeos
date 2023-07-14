import os
import asyncio
import secrets
import json
import time

from ipyeos.types import *
from ipyeos import eos, net, log
from ipyeos.chaintester import ChainTester
from ipyeos.transaction import Transaction

logger = log.get_logger(__name__)

def test_tx():
    t = ChainTester(False, log_level=5)
    tx = Transaction(int(time.time()), t.chain.head_block_id())
    tx.add_action('eosio.token', 'transfer', b'hello, world', {'eosio': 'active'})
    priv_key = PrivateKey.from_base58('5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3')
    tx.sign(priv_key, Checksum256.empty())
    raw_tx = tx.pack()
    logger.info(tx.id())
    logger.info(raw_tx)
    logger.info(Transaction.to_json(raw_tx, 0))
    logger.info(Transaction.to_json(raw_tx, 1))
