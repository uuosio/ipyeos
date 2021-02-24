import os
import time
import json
import platform

from uuosio.chaintester import ChainTester
from uuosio import log, uuos
logger = log.get_logger(__name__)

print(os.getpid())
input('<<<')

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
        uuos.enable_native_contracts(True)
        eosio_contract = f'build/libraries/vm_api//test/libnative_eosio_system2.{self.so}'
        ret = uuos.set_native_contract(uuos.s2n('eosio'), eosio_contract)
        assert ret

        logger.info(self.tester.api.get_account('hello'))
        self.tester.buy_ram_bytes('hello', 'hello', 10*1024*1024)
        logger.info(self.tester.api.get_account('hello'))

        uuos.enable_native_contracts(False)
        uuos.set_native_contract(uuos.s2n('eosio'), '')

