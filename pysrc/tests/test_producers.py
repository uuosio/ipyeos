import json
import logging
import os
import tempfile
from datetime import datetime, timedelta

import pytest

from ipyeos.chaintester import ChainTester

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(module)s %(lineno)d %(message)s')

logger=logging.getLogger(__name__)

class TestProducers(object):

    @classmethod
    def setup_class(cls):
        cls.tester = ChainTester()
        producers = ['hello', 'bob', 'alice']
        for p in producers:
            cls.tester.buy_ram_bytes(p, p, 64*1024)

    @classmethod
    def teardown_class(cls):
        cls.tester.free()

    def setup_method(self, method):
        logger.warning('test start: %s', method.__name__)

    def teardown_method(self, method):
        pass

    def test_hello(self):
        r = self.tester.push_action('eosio.mpy', 'hellompy', b'', {'alice':'active'})
        logger.info(r['action_traces'][0]['console'])

    def test_regprod(self):
        balance = self.tester.get_balance('eosio')
        balance *= 0.2 #over 15% threshold to activate chain
        self.tester.transfer('eosio', 'hello', balance)

        producers = ['hello', 'bob', 'alice']
        producers.sort()

        # register producer and staking
        for producer in producers:
            args = {
                "producer": producer,
                "producer_key":"EOS6AjF6hvF7GSuSd4sCgfPKq5uWaXvGM2aQtEUCwmEHygQaqxBSV",
                "url":"http://eos.io",
                "location":1
            }
            self.tester.push_action('eosio', 'regproducer', args, {producer:'active'})
        
        for producer in producers:
            self.tester.delegatebw('hello', producer, 0.0, balance/len(producers))
            self.tester.delegatebw(producer, producer, 0.0, 1.0)

        args = {
            "producer": 'helloworld11',
            "producer_key":"EOS6AjF6hvF7GSuSd4sCgfPKq5uWaXvGM2aQtEUCwmEHygQaqxBSV",
            "url":"http://eos.io",
            "location":1
        }
        self.tester.push_action('eosio', 'regproducer', args, {'helloworld11':'active'})

        # vote
        for producer in producers:
            args = dict(
                voter=producer,
                proxy='.',
                producers=producers
            )
            self.tester.push_action('eosio', 'voteproducer', args, {producer:'active'})

        # activate new producers
        for i in range(12):
            self.tester.produce_block()

        r = self.tester.api.get_producers(True, '.', 100)
        for info in r:
            logger.info(info)

        r = self.tester.api.get_producer_schedule()
        logger.info(r)
        for i in range(12):
            self.tester.produce_block()
        r = self.tester.api.get_producer_schedule()
        logger.info(r)

