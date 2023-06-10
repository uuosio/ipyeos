import json
import os
import platform
import time

from ipyeos import log
from ipyeos.chaintester import ChainTester

logger = log.get_logger(__name__)

# print(os.getpid())
# input('<<<')

class TestMicropython(object):

    @classmethod
    def setup_class(cls):
        cls.tester = ChainTester()
        args = {"account": 'hello',
            "vmtype": 1,
            "vmversion": 0,
            "code": int.to_bytes(int(time.time()*1000), 8, 'little').hex()
        }
        r = cls.tester.push_action('eosio', 'setcode', args, {'hello':'active'})

        if platform.system() == 'Linux':
            cls.so = 'so'
        else:
            cls.so = 'dylib'

    @classmethod
    def teardown_class(cls):
        cls.tester.free()

    def setup_method(self, method):
        logger.warning('test start: %s', method.__name__)

    def teardown_method(self, method):
        self.tester.produce_block()

    def test_mpy(self):
        code = '''
def apply(a, b, c):
    print('hello,world')
'''
        code = self.tester.mp_compile('hello', code)
        args = eos.s2b('hello') + code
        self.tester.push_action('hello', 'setcode', args, {'hello':'active'})
        r = self.tester.push_action('hello', 'sayhello', b'', {'hello':'active'})

        code = '''
def apply(a, b, c):
    print('hello,world from alice')
'''
        code = self.tester.mp_compile('hello', code)
        args = eos.s2b('alice') + code
        self.tester.push_action('hello', 'setcode', args, {'alice':'active'})

        args = eos.s2b('alice')
        r = self.tester.push_action('hello', 'exec', args, {'hello':'active'})
        logger.info(r['action_traces'][0]['console'])
        print(r['elapsed'])

    def test_setcode(self):
        r = self.tester.push_action('hello', 'hellompy', b'', {'hello':'active'})
        logger.info(r['action_traces'][0]['console'])

    def test_hello(self):
        r = self.tester.push_action('eosio.mpy', 'hellompy', b'', {'alice':'active'})
        logger.info(r['action_traces'][0]['console'])

    def test_debug(self):
        eos.enable_native_contracts(True)
        eosio_contract = f'eos/build/libraries/vm_api//test/libnative_eosio_system2.{self.so}'
        ret = eos.set_native_contract(eos.s2n('eosio'), eosio_contract)
        assert ret

        self.tester.buy_ram_bytes('eosio', 'hello', 10*1024*1024)

        r = self.tester.push_action('eosio.mpy', 'hellompy', b'', {'alice':'active'})
        logger.info(r['action_traces'][0]['console'])
        print(r['elapsed'])

        r = self.tester.push_action('eosio.mpy', 'hellompy', int.to_bytes(1, 8, 'little'), {'alice':'active'})
        logger.info(r['action_traces'][0]['console'])
        print(r['elapsed'])

        eos.enable_native_contracts(False)
        eos.set_native_contract(eos.s2n('eosio.mpy'), '')

    def test_setcode2(self):
        code = '/Users/newworld/dev/uuos3/externals/micropython/build/ports/micropython_eosio.wasm'
        with open(code, 'rb') as f:
            code = f.read()
        self.tester.deploy_code('eosio.mpy', code, vm_type=0)

        code = '''
def init(args):
    print(args)
def apply(a, b, c):
    print('hello,world')
'''
        code = self.tester.mp_compile('hello', code)
        args = eos.s2b('hello') + int.to_bytes(len(code), 4, 'little') + code + b'hello, init function'
        self.tester.push_action('hello', 'setcode2', args, {'hello':'active'})
        r = self.tester.push_action('hello', 'sayhello', b'', {'hello':'active'})
