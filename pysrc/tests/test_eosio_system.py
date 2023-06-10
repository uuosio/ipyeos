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

    def test_native_contract(self):
        eos.enable_native_contracts(True)
        eosio_contract = f'build/libraries/vm_api//test/libnative_eosio_system2.{self.so}'
        ret = eos.set_native_contract(eos.s2n('eosio'), eosio_contract)
        assert ret

        logger.info(self.tester.api.get_account('hello'))
        self.tester.buy_ram_bytes('hello', 'hello', 10*1024*1024)
        logger.info(self.tester.api.get_account('hello'))

        eos.enable_native_contracts(False)
        eos.set_native_contract(eos.s2n('eosio'), '')

    def test_mpy(self):
        code = '''
import example
def apply(a, b, c):
    print(example.add_ints(1, 2))
    example.say_hello()
    for i in range(10):
        print('hello,world')
'''
        code = self.tester.mp_compile('hello', code)
        args = eos.s2b('hello') + code
        r = self.tester.push_action('eosio', 'deploycode', args, {'hello':'active'})
        logger.info(r['action_traces'][0]['console'])


        args = eos.s2b('hello') + b'hello,world'
        r = self.tester.push_action('eosio', 'exec', args, {'hello':'active'})
        # logger.info('+++%s', r['action_traces'][0]['console'])
        logger.info('++++elapsed: %s', r['elapsed'])
