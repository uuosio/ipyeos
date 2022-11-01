import os
import hashlib
import platform

from ipyeos import eos
from ipyeos import chaintester
from ipyeos.chaintester import ChainTester

chaintester.chain_config['contracts_console'] = True

def test_example():
    t = ChainTester(True)
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
