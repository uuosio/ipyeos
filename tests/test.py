import os
import hashlib
import shutil
import platform

from ipyeos import eos, log
from ipyeos import chaintester
from ipyeos.chaintester import ChainTester

from ipyeos.chain_exceptions import ForkDatabaseException, ChainException, get_last_exception
from ipyeos.types import PublicKey
from ipyeos.database_objects import KeyWeight, Authority
from ipyeos.database import PermissionObjectIndex, GlobalPropertyObjectIndex
from ipyeos.block_log import BlockLog

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
    chain = chaintester.ChainTester(initialize, log_level=5)
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
    t = ChainTester(True, log_level=1)
    os.system('cd native;./build.sh')
    assert t.chain.set_native_contract("hello", so_file)
    with open('./hello/build/hello/hello.wasm', 'rb') as f:
        code = f.read()
    with open('./hello/build/hello/hello.abi', 'rb') as f:
        abi = f.read()
    t.deploy_contract('hello', code, abi)
    t.produce_block()

    eos.enable_debug(True)
    t.push_action('hello', 'hi', {'nm': 'alice'}, {'hello': 'active'})
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
    t = ChainTester(True, log_level=5)
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
    t = ChainTester(False, data_dir=os.path.join(dir_name, 'dd'), config_dir=os.path.join(dir_name, 'cd'), log_level=5)
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
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_dir=snapshot_dir, debug_producer_key=debug_producer_key, log_level=5)

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
    t = ChainTester(True, data_dir=os.path.join(data_name, 'dd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_dir=snapshot_dir, log_level=5)

    t.produce_block()
    logger.info("+++++++%s", t.api.get_info())
    t.free()


def test_push_block():
    if os.path.exists('./data/ddd'):
        shutil.rmtree('./data/ddd')

    state_size = 10*1024*1024
    data_name = './data'

    snapshot_dir = './data/push_block/snapshot-0000003b83662343c208e965654f4d906ed7fad0372e13c246981cd076d379bb.bin'
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_dir=snapshot_dir, log_level=5)
    t.free()

    snapshot_dir = ''
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_dir=snapshot_dir, log_level=5)
    t.chain.abort_block()

    info = t.api.get_info()
    head_block_num = info['head_block_num']
    blog = BlockLog('./data/push_block/blocks')
    logger.info("%s %s", head_block_num, blog.head_block_num())
    num_count = blog.head_block_num() - head_block_num

    for block_num in range(head_block_num+1, head_block_num+num_count+1):
        t.chain.push_block(blog, block_num)


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

def test_exception():
    exception = '''{"code": 3020000, "name": "fork_database_exception", "message": "Fork database exception", "stack": [{"context": {"level": "error", "file": "controller.cpp", "line": 2240, "method": "operator()", "hostname": "", "thread_name": "chain-1", "timestamp": "2023-07-11T15:56:40.581"}, "format": "we already know about this block: ${id}", "data": {"id": "0000003c175d15e908e364816194f6dd239102fd4a4c2f46f4e81f977012b42d"}}]}'''
    e = get_last_exception(exception)
    logger.info("++++++%s", e.stack[0].context.level)
    logger.info("++++++%s", e.stack[0].format)
    logger.info("++++++%s", e.stack[0].data)

def test_push_raw_block():
    if os.path.exists('./data/ddd'):
        shutil.rmtree('./data/ddd')

    state_size = 10*1024*1024
    data_name = './data'

    snapshot_file = './data/push_block/snapshot-0000003b83662343c208e965654f4d906ed7fad0372e13c246981cd076d379bb.bin'
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_file=snapshot_file, log_level=5)
    t.free()

    snapshot_dir = ''
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_file='', log_level=5)
    t.chain.abort_block()

    info = t.api.get_info()
    head_block_num = info['head_block_num']
    blog = BlockLog('./data/push_block/blocks')
    logger.info("%s %s", head_block_num, blog.head_block_num())
    num_count = blog.head_block_num() - head_block_num

    block_num = head_block_num+1
    block = blog.read_block_by_num(block_num)
    raw_block = eos.pack_block(block)
    t.chain.push_raw_block(raw_block)
    try:
        t.chain.push_raw_block(raw_block)
    except ForkDatabaseException as e:
        logger.info("++++++%s", e)
        logger.info("++++++%s", e.stack[0].context)
        logger.info("++++++%s", e.stack[0].format)
        # assert e.stack[0]['context'].format.startswith('we already know about this block')

    for block_num in range(head_block_num+2, head_block_num+num_count+1):
        block = blog.read_block_by_num(block_num)
        raw_block = eos.pack_block(block)
        t.chain.push_raw_block(raw_block)


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
    t = ChainTester(False, log_level=5)
    action = ['eosio', 'sayhello', b'hello, world', {'eosio':'active'}]
    tx = t.gen_transaction([action], json_str=True)
    logger.info(tx)

    tx = t.gen_transaction([action], json_str=False, compress=True)
    logger.info(eos.unpack_transaction(tx))
