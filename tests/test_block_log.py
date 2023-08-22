import os
import hashlib
import shutil
import sys
import platform
import time

from ipyeos import eos, log
from ipyeos import chaintester
from ipyeos.chaintester import ChainTester

from ipyeos.chain_exceptions import BlockValidateException, ChainException, ForkDatabaseException, get_last_exception
from ipyeos.block_log import BlockLog
from ipyeos.signed_block import SignedBlock

chaintester.chain_config['contracts_console'] = True
dir_name = os.path.dirname(__file__)

logger = log.get_logger(__name__)

def update_auth(chain, account):
    a = {
        "account": account,
        "permission": "active",
        "parent": "owner",
        "auth": {
            "threshold": 1,
            "keys": [
                {
                    "key": 'EOS6AjF6hvF7GSuSd4sCgfPKq5uWaXvGM2aQtEUCwmEHygQaqxBSV',
                    "weight": 1
                }
            ],
            "accounts": [{"permission":{"actor":account,"permission": 'eosio.code'}, "weight":1}],
            "waits": []
        }
    }
    chain.push_action('eosio', 'updateauth', a, {account:'active'})

def init_chain(initialize=True):
    chain = chaintester.ChainTester(initialize)
    # update_auth(chain, 'hello')
    return chain

def chain_test(initialize=True):
    def init_call(fn):
        def call(*args, **vargs):
            chain = init_chain(initialize)
            ret = fn(chain, *args, **vargs)
            chain.free()
            return ret
        return call
    return init_call

def test_push_block_from_block_log():
    if os.path.exists('./data/ddd'):
        shutil.rmtree('./data/ddd')

    state_size = 10*1024*1024
    data_name = './data'

    snapshot_file = './data/push_block/snapshot-0000003b83662343c208e965654f4d906ed7fad0372e13c246981cd076d379bb.bin'
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_file=snapshot_file)
    t.free()

    snapshot_file = ''
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size)
    t.chain.abort_block()

    info = t.api.get_info()
    head_block_num = info['head_block_num']
    blog = BlockLog('./data/push_block/blocks')
    logger.info("%s %s", head_block_num, blog.head_block_num())
    num_count = blog.head_block_num() - head_block_num

    for block_num in range(head_block_num+1, head_block_num+num_count+1):
        t.chain.push_block_from_block_log(blog, block_num)


    block = blog.read_block_by_num(blog.head_block_num())
    logger.info("++++block: %s", block)

    block_header = blog.read_block_header_by_num(blog.head_block_num())
    logger.info("++++block_header: %s", block_header)

    block_id = blog.read_block_id_by_num(blog.head_block_num())
    logger.info("++++block_id: %s", block_id)
    

    info = t.api.get_info()
    logger.info("+++++++%s %s", head_block_num, info['head_block_num'])
    assert head_block_num + num_count == info['head_block_num']
    t.free()

def test_push_block():
    if os.path.exists('./data/ddd'):
        shutil.rmtree('./data/ddd')

    state_size = 10*1024*1024
    data_name = './data'

    snapshot_file = './data/push_block/snapshot-0000003b83662343c208e965654f4d906ed7fad0372e13c246981cd076d379bb.bin'
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_file=snapshot_file)
    t.free()

    snapshot_dir = ''
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_file='')
    t.chain.abort_block()

    info = t.api.get_info()
    head_block_num = info['head_block_num']
    blog = BlockLog('./data/push_block/blocks')

    logger.info("%s %s", head_block_num, blog.head_block_num())
    num_count = blog.head_block_num() - head_block_num

    block_num = head_block_num+1
    block = blog.read_block_by_num(block_num)
    # raw_block = block.pack()
    t.chain.push_block(block)
    try:
        t.chain.push_block(block)
    except ForkDatabaseException as e:
        logger.info("++++++%s", e)
        logger.info("++++++%s", e.json()['stack'][0]['context'])
        logger.info("++++++%s", e.json()['stack'][0]['format'])
        # assert e.stack[0]['context'].format.startswith('we already know about this block')

    for block_num in range(head_block_num+2, head_block_num+num_count+1):
        block = blog.read_block_by_num(block_num)
        # raw_block = block.pack()
        t.chain.push_block(block)

    block = blog.read_block_by_num(blog.head_block_num())
    logger.info("++++block: %s", block)

    block_header = blog.read_block_header_by_num(blog.head_block_num())
    logger.info("++++block_header: %s", block_header)

    block_id = blog.read_block_id_by_num(blog.head_block_num())
    logger.info("++++block_id: %s", block_id)
    

    info = t.api.get_info()
    logger.info("+++++++%s %s", head_block_num, info['head_block_num'])
    assert head_block_num + num_count == info['head_block_num']
    t.free()

    block = blog.head()
    logger.info("%s", block)
    raw = block.pack()
    assert raw == SignedBlock.unpack(raw).pack()


