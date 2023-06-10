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

class TestPowerup(object):

    @classmethod
    def setup_class(cls):
        cls.tester = ChainTester()
        cls.tester.buy_ram_bytes('eosio', 'eosio.reserv', 64*1024)

        args = {
        "cpu": {
            "current_weight_ratio":"10000000000000", # use default current_weight_ratio
            "target_weight_ratio": "10000000000000",
            "assumed_stake_weight": 3717015416,
            "target_timestamp": "2021-02-18T12:35:24",
            "exponent": 2,
            "decay_secs": 86400,
            "max_price": "1075000.0000 UUOS",
            "min_price": "2500.0000 UUOS",

            "adjusted_utilization": 1215803671,
            "initial_timestamp": "2021-02-13T14:35:24",
            "initial_weight_ratio": "10000000000000",
            "utilization": 1210869642,
            "utilization_timestamp": "2021-02-13T14:35:24",
            "version": 0,
            "weight": "367984526184",
            "weight_ratio": "10000000000000"
        },
        "min_powerup_fee": "0.0001 UUOS",
        "net": {
            "current_weight_ratio":"10000000000000", # use default current_weight_ratio
            "target_weight_ratio": "10000000000000",
            "assumed_stake_weight": 929253854,
            "target_timestamp": "2021-02-18T12:35:24",
            "exponent": 2,
            "decay_secs": 86400,
            "max_price": "95000.0000 UUOS",
            "min_price": "2500.0000 UUOS",

            "adjusted_utilization": 98566186,
            "initial_timestamp": "2021-02-13T14:35:24",
            "initial_weight_ratio": "10000000000000",
            "utilization": 98566186,
            "utilization_timestamp": "2021-02-13T14:35:24",
            "version": 0,
            "weight": "91996131546",
            "weight_ratio": "10000000000000"
        },
        "powerup_days": 1,
        "version": 0
        }

        r = cls.tester.push_action('eosio', 'cfgpowerup', {'args':args}, {'eosio':'active'})
        cls.tester.produce_block()

    @classmethod
    def teardown_class(cls):
        cls.tester.free()

    def setup_method(self, method):
        logger.warning('test start: %s', method.__name__)

    def teardown_method(self, method):
        pass

    def test_powerup(self):
        account = 'alice'
        args = {
            'payer':account,
            'receiver':account,
            'days':1,
            'net_frac':1e7,
            'cpu_frac':1e7,
            'max_payment':'1.0000 UUOS'
        }
        self.tester.push_action('eosio', 'powerup', args, {account:'active'})

    def test_hello(self):
        r = self.tester.push_action('eosio.mpy', 'hellompy', b'', {'alice':'active'})
        logger.info(r['action_traces'][0]['console'])

