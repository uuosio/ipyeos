import os
import asyncio
import secrets
import json
import time

from ipyeos.chaintester import ChainTester
from ipyeos.block_state import BlockState

def on_accepted_block(block_state_ptr):
    # print("on_accepted_block", block_state_ptr)
    bs = BlockState(block_state_ptr)
    print("block_num", bs.get_block_num())
    bs.free()

def test_on_accepted_block():
    t = ChainTester()
    t.chain.set_accepted_block_callback(on_accepted_block)

    for i in range(20):
        t.produce_block()

    print(t.chain.head_block_num())

