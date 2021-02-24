import os
import time
import json
import platform

from uuosio.chaintester import ChainTester
from uuosio import log, uuos
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
        args = uuos.s2b('hello') + code
        self.tester.push_action('hello', 'setcode', args, {'hello':'active'})
        r = self.tester.push_action('hello', 'sayhello', b'', {'hello':'active'})

        code = '''
def apply(a, b, c):
    print('hello,world from alice')
'''
        code = self.tester.mp_compile('hello', code)
        args = uuos.s2b('alice') + code
        self.tester.push_action('hello', 'setcode', args, {'alice':'active'})

        args = uuos.s2b('alice')
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
        uuos.enable_native_contracts(True)
        eosio_contract = f'build/libraries/vm_api//test/libnative_eosio_system2.{self.so}'
        ret = uuos.set_native_contract(uuos.s2n('eosio'), eosio_contract)
        assert ret

        self.tester.buy_ram_bytes('eosio', 'hello', 10*1024*1024)

        r = self.tester.push_action('eosio.mpy', 'hellompy', b'', {'alice':'active'})
        logger.info(r['action_traces'][0]['console'])
        print(r['elapsed'])

        r = self.tester.push_action('eosio.mpy', 'hellompy', int.to_bytes(1, 8, 'little'), {'alice':'active'})
        logger.info(r['action_traces'][0]['console'])
        print(r['elapsed'])

        uuos.enable_native_contracts(False)
        uuos.set_native_contract(uuos.s2n('eosio.mpy'), '')

