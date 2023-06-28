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
    tx = Transaction(int(time.time()), t.chain.head_block_id)
    tx.add_action('eosio.token', 'transfer', b'hello, world', {'eosio': 'active'})
    base58_priv_key = '5JRYimgLBrRLCBAcjHUWCYRv3asNedTYYzVgmiU4q2ZVxMBiJXL'
    priv_key = PrivateKey.from_base58(base58_priv_key)
    logger.info(priv_key.to_base58() == base58_priv_key)
    tx.sign(priv_key, Checksum256.empty())
    logger.info(tx.pack())
    logger.info(Transaction.unpack(tx.pack(), 0))
    logger.info(Transaction.unpack(tx.pack(), 1))
