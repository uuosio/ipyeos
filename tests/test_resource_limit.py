import os
import asyncio
import secrets
import json
import time

from ipyeos.types import *
from ipyeos import eos, net, log
from ipyeos.tester.chaintester import ChainTester
from ipyeos.resource_limit import ResourceLimit

logger = log.get_logger(__name__)

def test_limit():
    t = ChainTester(False)
    limit = ResourceLimit(t.db)
    logger.info(limit.get_total_cpu_weight())

    logger.info('+++total_cpu_weight: %s', limit.get_total_cpu_weight())
    logger.info('+++total_net_weight: %s', limit.get_total_net_weight())
    logger.info('+++virtual_block_cpu_limit: %s', limit.get_virtual_block_cpu_limit())
    logger.info('+++virtual_block_net_limit: %s', limit.get_virtual_block_net_limit())
    logger.info('+++block_cpu_limit: %s', limit.get_block_cpu_limit())
    logger.info('+++block_net_limit: %s', limit.get_block_net_limit())
    logger.info('+++is_unlimited_cpu: %s', limit.is_unlimited_cpu('eosio'))
    logger.info('+++get_account_limits: %s', limit.get_account_limits('eosio'))
    logger.info('+++get_account_ram_usage: %s', limit.get_account_ram_usage('eosio'))
