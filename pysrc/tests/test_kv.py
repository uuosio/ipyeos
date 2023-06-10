import json
import os
import platform
import time

from ipyeos import log
from ipyeos.chaintester import ChainTester

logger = log.get_logger(__name__)

# print(os.getpid())
# input('<<<')

test_dir = os.path.dirname(__file__)

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
        
        with open(os.path.join(test_dir, 'activate_kv.wasm'), 'rb') as f:
            code = f.read()
            cls.tester.deploy_contract('alice', code, b'')
        cls.tester.push_action('eosio', 'setpriv', {'account':'alice', 'is_priv':True})
        cls.tester.push_action('alice', 'setkvparams', b'')
        cls.tester.push_action('eosio', 'setpriv', {'account':'alice', 'is_priv':False})

        args = {"account": 'alice',
            "vmtype": 1,
            "vmversion": 0,
            "code": int.to_bytes(int(time.time()*1000), 8, 'little').hex()
        }
        r = cls.tester.push_action('eosio', 'setcode', args, {'alice':'active'})

        cls.tester.produce_block()

    @classmethod
    def teardown_class(cls):
        cls.tester.free()

    def setup_method(self, method):
        logger.warning('test start: %s', method.__name__)

    def teardown_method(self, method):
        self.tester.produce_block()

    def test_1(self):
        with open(os.path.join(test_dir, 'test_contracts/kv.py'), 'r') as f:
            code = f.read()
        code = self.tester.mp_compile('alice', code)
        args = eos.s2b('alice') + code
        self.tester.push_action('alice', 'setcode', args, {'alice':'active'})
        r = self.tester.push_action('alice', 'sayhello', b'', {'alice':'active'})
        logger.info('+++elapsed: %s', r['elapsed'])

    def test_2(self):
        code = '''
def apply(a, b, c):
    a = float128('3.14') * 5.1
    print(type(a), a)

    a = 5.1 * float128('3.14')
    print(type(a), a)

    a = float128(3.14) * float128(5.1)
    print(type(a), a)

    raw_bytes = bytes(float128(3.14))
    print(raw_bytes)
    print(float128(raw_bytes))
'''
        account = 'eosio.mpy'
        account = 'alice'
        code = self.tester.mp_compile(account, code)
        args = eos.s2b(account) + code
        self.tester.push_action(account, 'setcode', args, {account:'active'})
        args = eos.s2b(account)
        r = self.tester.push_action(account, 'exec3', args, {account:'active'})
        logger.info('+++elapsed: %s', r['elapsed'])
        self.tester.produce_block()

    def test_hello(self):
        r = self.tester.push_action('eosio.mpy', 'hellompy', b'', {'alice':'active'})
        logger.info(r['action_traces'][0]['console'])
