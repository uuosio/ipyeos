import os
import hashlib
import shutil
import sys
import platform
import pytest
import time
import tempfile

from ipyeos import eos
from ipyeos.bases import log
from ipyeos.tester import chaintester
from ipyeos.tester.chaintester import ChainTester

from ipyeos.core.chain_exceptions import BlockValidateException, ChainException, ForkDatabaseException, get_last_exception
from ipyeos.bases.types import PublicKey
from ipyeos.core.database_objects import KeyWeight, Authority
from ipyeos.core.database import PermissionObjectIndex, GlobalPropertyObjectIndex
from ipyeos.core.block_log import BlockLog
from ipyeos.extensions.trace_api import TraceAPI

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

@chain_test(True)
def test_example(t: ChainTester):
    with open('./hello/hello.wasm', 'rb') as f:
        code = f.read()
    with open('./hello/hello.abi', 'rb') as f:
        abi = f.read()
    t.deploy_contract('hello', code, abi)
    t.produce_block()

    t.push_action('hello', 'hi', {'nm': 'alice'}, {'hello': 'active'})
    t.produce_block()

def test_basic():
    key = eos.create_key()
    priv_key = key['private']
    print(eos.get_public_key(priv_key))
    digest = hashlib.sha256(b'Hello World').hexdigest()
    # digest = digest.upper()
    print(digest, priv_key)
    signature = eos.sign_digest(digest, priv_key)
    print(signature)

def test_load_native_lib():
    if platform.system() == 'Darwin':
        so_file = 'native/build/libnative.dylib'
    else:
        so_file = 'native/build/libnative.so'
    t = ChainTester(True)
    os.system('cd native;./build.sh')
    assert t.chain.set_native_contract("hello", so_file)
    with open('./hello/build/hello/hello.wasm', 'rb') as f:
        code = f.read()
    with open('./hello/build/hello/hello.abi', 'rb') as f:
        abi = f.read()
    t.deploy_contract('hello', code, abi)
    t.produce_block()

    eos.enable_debug(True)
    t.push_action('hello', 'hi', eos.s2b('hello'), {'hello': 'active'})
    t.produce_block()


    assert not t.chain.set_native_contract("hello", so_file + 'xx')
    assert t.chain.set_native_contract("alice", so_file)
    os.system('cd native;touch native.c;./build.sh')
    # trigger reloading
    assert t.chain.set_native_contract("hello", so_file)
    assert t.chain.set_native_contract("hello", "")

def test_hello():
    os.system('mkdir hello/build;cd hello/build;cmake -Dcdt_DIR=`cdt-get-dir` ..;make')
    eos.enable_debug(True)
    t = ChainTester(True)
    with open('./hello/build/hello/hello.wasm', 'rb') as f:
        code = f.read()
    with open('./hello/build/hello/hello.abi', 'rb') as f:
        abi = f.read()
    t.deploy_contract('hello', code, abi)
    t.produce_block()

    t.push_action('hello', 'hi', {'nm': 'alice'}, {'hello': 'active'})
    t.produce_block()

# def test_http_client():
#     from ipyeos.interfaces import IPCChainTester

#     from thrift.transport import THttpClient
#     from thrift.transport import TTransport
#     from thrift.protocol import TBinaryProtocol

#     transport = THttpClient.THttpClient('http://localhost:9094')
#     transport = TTransport.TBufferedTransport(transport)
#     protocol = TBinaryProtocol.TBinaryProtocol(transport)
#     client = IPCChainTester.Client(protocol)

#     # Connect!
#     transport.open()
#     ret = client.create_key("K1")
#     print(ret)

# print(os.getpid())
# input('press any key to continue...')

def test_custom_dir():
    t = ChainTester(False, data_dir=os.path.join(dir_name, 'dd'), config_dir=os.path.join(dir_name, 'cd'))
    t.produce_block()
    logger.info("+++++++%s", t.api.get_info())

def test_custom_2dir():
    # data_name = './data'
    # snapshot_dir = './snapshot-2023-06-18-01-eos-v6-0315729695.bin'
    # state_size = 32*1024*1024*1024
    if os.path.exists('./data/ddd'):
        shutil.rmtree('./data/ddd')
    state_size = 10*1024*1024
    data_name = './data'
    snapshot_dir = './data/snapshot-0000001ba25b3b5af4ba6cacecb68ef4238a50bb7134e56fe985b4355fbf7488.bin'

    # {'private': '5K3x5DPEbocfZSG8XD3RiyJAfPFH5Bd9ED15wtdEMbqzXCLPbma',
    #  'public': 'EOS5K93aPtTdov2zWDqYxVcMQ4GBT1hyEpED8tjzPuLsf31tPySNY'}

    chaintester.import_producer_key('5K3x5DPEbocfZSG8XD3RiyJAfPFH5Bd9ED15wtdEMbqzXCLPbma')
    debug_producer_key = 'EOS5K93aPtTdov2zWDqYxVcMQ4GBT1hyEpED8tjzPuLsf31tPySNY'
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_file=snapshot_dir, debug_producer_key=debug_producer_key)

    idx = GlobalPropertyObjectIndex(t.db)
    obj = idx.get()
    if obj.proposed_schedule_block_num:
        # reset proposed schedule producers
        obj.proposed_schedule.producers = []
        obj.proposed_schedule_block_num = None
        idx.set(obj)

    logger.info("+++++producer keys: %s", t.chain.get_producer_public_keys())
    t.produce_block()
    logger.info("+++++++%s", t.api.get_info())

    idx = PermissionObjectIndex(t.db)
    perm = idx.find_by_owner('eosio.token', 'active')
    print(perm)

    # Private key: 5JBW9jddvqHY7inGEK2qWbGLYKeqm32NDYL3fLdYgMjnWxRjXLF
    # Public key: EOS6hM1U89jbHWyX8ArHttFzoGe21y7ehXvtN5q7GbDxYEa9NFXH2
    t.import_key('5JBW9jddvqHY7inGEK2qWbGLYKeqm32NDYL3fLdYgMjnWxRjXLF')
    keys = [KeyWeight(PublicKey.from_base58('EOS6hM1U89jbHWyX8ArHttFzoGe21y7ehXvtN5q7GbDxYEa9NFXH2'), 1)]
    perm.auth = Authority(1, keys, [], [])

    ret = idx.modify(perm)
    print('modify_by_id return:', ret)

    idx = PermissionObjectIndex(t.db)
    perm = idx.find_by_owner('eosio.token', 'active')
    print(perm)

    t.free()

    snapshot_dir = ''

    # {'private': '5K3x5DPEbocfZSG8XD3RiyJAfPFH5Bd9ED15wtdEMbqzXCLPbma',
    #  'public': 'EOS5K93aPtTdov2zWDqYxVcMQ4GBT1hyEpED8tjzPuLsf31tPySNY'}

    chaintester.import_producer_key('5K3x5DPEbocfZSG8XD3RiyJAfPFH5Bd9ED15wtdEMbqzXCLPbma')
    t = ChainTester(True, data_dir=os.path.join(data_name, 'dd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_file=snapshot_dir)

    t.produce_block()
    logger.info("+++++++%s", t.api.get_info())
    t.free()

def test_exception():
    exception = '''{"code": 3020000, "name": "fork_database_exception", "message": "Fork database exception", "stack": [{"context": {"level": "error", "file": "controller.cpp", "line": 2240, "method": "operator()", "hostname": "", "thread_name": "chain-1", "timestamp": "2023-07-11T15:56:40.581"}, "format": "we already know about this block: ${id}", "data": {"id": "0000003c175d15e908e364816194f6dd239102fd4a4c2f46f4e81f977012b42d"}}]}'''
    e = get_last_exception(exception)
    logger.info("++++++%s", e.json()['stack'][0]['context']['level'])
    logger.info("++++++%s", e.json()['stack'][0]['format'])
    logger.info("++++++%s", e.json()['stack'][0]['data'])

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

def test_gen_tx():
    t = ChainTester(False)
    action = ['eosio', 'sayhello', b'hello, world', {'eosio':'active'}]
    tx = t.gen_transaction([action], json_str=True)
    logger.info(tx)

    tx = t.gen_transaction([action], json_str=False, compress=True)
    logger.info(eos.unpack_transaction(tx))

def test_abort_block():
    t = ChainTester(False)
    try:
        t.chain.start_block()
    except BlockValidateException as e:
        logger.error(e.json()['stack'][0]['format'])
    t.chain.abort_block()
    t.chain.abort_block()

@chain_test(True)
def test_start_block(t: ChainTester):
    # if 'pytest' in sys.modules:
    #     print('in pytest')
    #     return
    t.chain.abort_block()
    count = 1000
    txs = []
    for i in range(count):
        action = {
            'account': 'hello',
            'name': 'hi',
            'data': b'hi'.hex() + str(i).encode().hex(),
            'authorization': [{'actor':'hello', 'permission':'active'}]
        }
        ret = t.gen_transaction_ex([action])
        txs.append(ret)

    start = time.monotonic()

    for tx in txs:
        t.chain.start_block()
        t.chain.push_transaction(tx)
        t.chain.abort_block()

    end = time.monotonic()
    logger.info("++++++OPS: %s", count/(end - start))
    return

@chain_test(True)
def test_trace(t: ChainTester):
    # if 'pytest' in sys.modules:
    #     print('in pytest')
    #     return
    trace = TraceAPI(t.chain, f'{t.data_dir}/trace')
    num = t.chain.head_block_num()
    for i in range(10):
        t.push_action('hello', 'hi', b'hi', {'hello': 'active'})
        t.produce_block()
    info = trace.get_block_trace(num + 1)
    logger.info(info)

def test_fork():
    logger.info("+++++==test_fork")
    eos.enable_adjust_cpu_billing(True)
    eos.set_info_level('default')

    t1 = ChainTester(True)
    t2 = ChainTester(False)
    t2.chain.abort_block()

    for num in range(2, t1.chain.head_block_num() + 1):
        block = t1.chain.fetch_block_by_number(num)
        t2.chain.push_block(block)

    t1.push_action('hello', 'hi', b'hi', {'hello': 'active'})    
    t1.produce_block()
    t1.produce_block()

    t2.start_block()
    t2.produce_block()
    t2.chain.abort_block()

    logger.info("%s %s", t1.chain.head_block_id(), t2.chain.head_block_id())
    num = t2.chain.head_block_num()

    block = t1.chain.fetch_block_by_number(num)
    logger.info(f"+++++++push block {num}")
    t2.chain.push_block(block)

    num += 1
    block = t1.chain.fetch_block_by_number(num)
    logger.info(f"+++++++push block {num}")
    t2.chain.push_block(block)

    logger.info("%s %s", t1.chain.head_block_id(), t2.chain.head_block_id())


    t1.produce_block()
    t1.chain.free()

    blog = BlockLog(f'{t1.data_dir}/blocks')    
    logger.info(blog.head_block_num())

def rent_cpu(t, account, cpu_frac):
    account = account
    args = {
        'payer':account,
        'receiver': account,
        'days':1,
        'net_frac':111460*2,
        'cpu_frac': cpu_frac,
        'max_payment':'1.1000 EOS'
    }
    try:
        r = t.push_action('eosio', 'powerup', args, {account:'active'})
        logger.info("+++++++++powerup: %s %s", r['elapsed'], r['receipt']['cpu_usage_us'])
        t.produce_block()
    except ChainException as e:
        raise e

from ipyeos.core.database import *

def load_data(db, contract):
    table_ids = []
    count = 0
    def on_data(raw_obj, user_data):
        nonlocal count
        count += 1
        # dec = Decoder(raw_obj)
        # obj = TableIdObject.unpack(dec)
        # logger.info("+++++table_id: %s, obj: %s", obj.table_id, obj)
        # return True
        table_id = int.from_bytes(raw_obj[0:8], 'little')
        table_ids.append(table_id)
        if len(table_ids) % 10000 == 0:
            logger.info("len(table_ids): %s", len(table_ids))
            # return 0
        return 1

    table_id_index = TableIdObjectIndex(db)
    table_id_index.walk_range_by_code_scope_table((contract, '', ''), (contract, 'zzzzzzzzzzzzj', 'zzzzzzzzzzzzj'), on_data, raw_data=True)

    def on_data2(obj, user_data):
        # print(obj)
        return 1

    logger.info("len(table_ids): %s", len(table_ids))

    logger.info("len(table_ids): %s", len(table_ids))
    key_value_index = KeyValueObjectIndex(db)    
    logger.info("walk KeyValueObject")
    # for table_id in table_ids:
    #     key_value_index.walk_range_by_scope_primary((table_id, 0), (table_id, 0xffffffffffffffff), on_data2, raw_data=True)

    indexes = [
        Index64ObjectIndex,
        Index128ObjectIndex,
        Index256ObjectIndex,
        IndexDoubleObjectIndex,
    ]
    for index in indexes:
        logger.info('index: %s', index.__name__)
        idx = index(db)
        for table_id in table_ids:
            idx.walk_range_by_secondary((table_id, 0, 0), (table_id, 0xffffffffffffffff, 0xffffffffffffffff), on_data2, raw_data=True)

    logger.info('index: %s', IndexLongDoubleObjectIndex.__name__)
    idx = IndexLongDoubleObjectIndex(db)
    for table_id in table_ids:
        idx.walk_range_by_secondary((table_id, F128(bytes(16)), 0), (table_id, F128(b'\xff'*16), 0xffffffffffffffff), on_data2, raw_data=True)

def update_permissions(t, test_account):
    idx = GlobalPropertyObjectIndex(t.db)
    obj = idx.get()
    if obj.proposed_schedule_block_num:
        # reset proposed schedule producers
        obj.proposed_schedule.producers = []
        obj.proposed_schedule_block_num = None
        idx.set(obj)

    logger.info("+++++producer keys: %s", t.chain.get_producer_public_keys())
    t.produce_block()
    logger.info("+++++++%s", t.api.get_info())

    idx = PermissionObjectIndex(t.db)
    perm = idx.find_by_owner('eosio.token', 'active')
    print(perm)

    keys = [KeyWeight(PublicKey.from_base58('EOS6hM1U89jbHWyX8ArHttFzoGe21y7ehXvtN5q7GbDxYEa9NFXH2'), 1)]
    perm.auth = Authority(1, keys, [], [])

    ret = idx.modify(perm)
    print('modify_by_id return:', ret)

    idx = PermissionObjectIndex(t.db)
    perm = idx.find_by_owner(test_account, 'active')
    keys = [KeyWeight(PublicKey.from_base58('EOS6hM1U89jbHWyX8ArHttFzoGe21y7ehXvtN5q7GbDxYEa9NFXH2'), 1)]
    perm.auth = Authority(1, keys, [], [])

    ret = idx.modify(perm)
    print('modify_by_id return:', ret)

@pytest.mark.skip(reason="Ignore this test for now.")
def test_debug_mainnet():
    eos.enable_adjust_cpu_billing(True)

    state_size = 32*1024*1024*1024
    chaintester.import_producer_key('5K3x5DPEbocfZSG8XD3RiyJAfPFH5Bd9ED15wtdEMbqzXCLPbma')
    debug_producer_key = 'EOS5K93aPtTdov2zWDqYxVcMQ4GBT1hyEpED8tjzPuLsf31tPySNY'
    data_dir = '/root/dev/dd'
    config_dir='/root/dev/cd'
    t = ChainTester(True, data_dir = data_dir, config_dir=config_dir, state_size=state_size, debug_producer_key=debug_producer_key)
    eos.set_info_level('default')

    # logger.info("+++load eosio contract")
    # load_data(t.db, 'eosio')

    # logger.info("+++load eosio.token contract")
    # load_data(t.db, 'eosio.token')

    test_account = 'helloworld11'

    idx = PermissionObjectIndex(t.db)
    perm = idx.find_by_owner('eosio.token', 'active')
    print(perm)

    # Private key: 5JBW9jddvqHY7inGEK2qWbGLYKeqm32NDYL3fLdYgMjnWxRjXLF
    # Public key: EOS6hM1U89jbHWyX8ArHttFzoGe21y7ehXvtN5q7GbDxYEa9NFXH2
    t.import_key('5JBW9jddvqHY7inGEK2qWbGLYKeqm32NDYL3fLdYgMjnWxRjXLF')

    update_permissions(t, test_account)

    args = {
        'from':'eosio.token',
        'to':test_account,
        'quantity':'100.0000 EOS',
        'memo':'hello'
    }
    for i in range(1):
        args['memo'] = str(i)
        logger.info("+++++++++transfer: %s", args)
        r = t.push_action('eosio.token', 'transfer', args, {'eosio.token':'active'})
        logger.info("+++++++++transfer finished %s %s", r['elapsed'], r['receipt']['cpu_usage_us'])
    t.produce_block()

    args = {"payer": 'eosio.token', "receiver": test_account, "bytes":100*1024}
    t.push_action('eosio', 'buyrambytes', args, {'eosio.token':'active'})

    logger.info("%s", t.get_account(test_account)['cpu_limit'])

    for i in range(10):
        rent_cpu(t, test_account, (88282981+i)*1000)
        logger.info("%s %s %s", t.get_account(test_account)['cpu_limit'], t.chain.head_block_num(), t.chain.last_irreversible_block_id())

    args = {
        'from':test_account,
        'to':'eosio.token',
        'quantity':'0.1000 EOS',
        'memo':'hello'
    }
    r = t.push_action('eosio.token', 'transfer', args, {test_account:'active'})
    logger.info("+++++++++transfer finished %s %s", r['elapsed'], r['receipt']['cpu_usage_us'])
    for i in range(2):
        t.produce_block()
        logger.info("%s", t.chain.last_irreversible_block_id())
        logger.info("%s", t.api.get_info())
