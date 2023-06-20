import os
import hashlib
import platform

from ipyeos import eos, log
from ipyeos import chaintester
from ipyeos.chaintester import ChainTester

from ipyeos.types import PublicKey
from ipyeos.database_objects import KeyWeight, Authority
from ipyeos.database_objects import PermissionObject, PermissionObjectIndex, Encoder, Decoder

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
    with open('./hello/build/hello/hello.wasm', 'rb') as f:
        code = f.read()
    with open('./hello/build/hello/hello.abi', 'rb') as f:
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
    signature = eos.sign_digest(priv_key, digest)
    print(signature)

def test_load_native_lib():
    if platform.system() == 'Darwin':
        so_file = 'native/build/libnative.dylib'
    else:
        so_file = 'native/build/libnative.so'
    t = ChainTester(False)
    os.system('cd native;./build.sh')
    assert t.chain.set_native_contract("hello", so_file)
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

    state_size = 10*1024*1024
    data_name = './data'
    snapshot_dir = './data/snapshot-0000001ba25b3b5af4ba6cacecb68ef4238a50bb7134e56fe985b4355fbf7488.bin'

    # {'private': '5K3x5DPEbocfZSG8XD3RiyJAfPFH5Bd9ED15wtdEMbqzXCLPbma',
    #  'public': 'EOS5K93aPtTdov2zWDqYxVcMQ4GBT1hyEpED8tjzPuLsf31tPySNY'}

    # must call set_debug_producer_key and import_producer_key before create ChainTester
    eos.set_debug_producer_key('EOS5K93aPtTdov2zWDqYxVcMQ4GBT1hyEpED8tjzPuLsf31tPySNY')
    chaintester.import_producer_key('5K3x5DPEbocfZSG8XD3RiyJAfPFH5Bd9ED15wtdEMbqzXCLPbma')

    t = ChainTester(True, data_dir=os.path.join(data_name, 'dd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_dir=snapshot_dir)
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

    ret = idx.modify_by_id(perm.table_id, perm)
    print('modify_by_id return:', ret)

    idx = PermissionObjectIndex(t.db)
    perm = idx.find_by_owner('eosio.token', 'active')
    print(perm)


def test_custom_3dir():
    state_size = 10*1024*1024
    data_name = './data'
    snapshot_dir = ''

    # {'private': '5K3x5DPEbocfZSG8XD3RiyJAfPFH5Bd9ED15wtdEMbqzXCLPbma',
    #  'public': 'EOS5K93aPtTdov2zWDqYxVcMQ4GBT1hyEpED8tjzPuLsf31tPySNY'}

    chaintester.import_producer_key('5K3x5DPEbocfZSG8XD3RiyJAfPFH5Bd9ED15wtdEMbqzXCLPbma')
    t = ChainTester(True, data_dir=os.path.join(data_name, 'dd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_dir=snapshot_dir)

    t.produce_block()
    logger.info("+++++++%s", t.api.get_info())
