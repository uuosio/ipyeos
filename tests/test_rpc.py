import json
import logging
import pytest
import requests
import time

from ipyeos import eos
from ipyeos.bases.types import PrivateKey
from ipyeos.core.signed_transaction import SignedTransaction
from ipyeos.core.chain_exceptions import AssertException

logger = logging.getLogger(__name__)


def test_trace_api():
    args = {'block_num': 1100}
    ret = requests.post('http://127.0.0.1:8088/get_block_trace', json=args)
    # ret = requests.post('http://127.0.0.1:8088/v1/trace_api/get_block', json=args)
    # ret = requests.post('http://localhost:8088/v1/trace_api/get_block', json=args)   
    # ret = requests.get('http://127.0.0.1:8088/v1/chain/get_info')   
    logger.info(ret.text)

def test_3rpc():
    import http.client
    import socket

    def get_request_over_unix_socket(socket_path, url_path):
        # Connect to the Unix socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(socket_path)

        # Create an HTTPConnection that uses this socket
        conn = http.client.HTTPConnection(host='localhost', port=None)
        conn.sock = sock

        # Send a GET request
        conn.request('GET', url_path)

        response = conn.getresponse()
        print(response.status, response.reason)
        print(response.read().decode())

    get_request_over_unix_socket('/tmp/uvicorn.sock', '/get_info')

@pytest.mark.asyncio
async def test_4rpc():
    import asyncio
    import aiohttp
    async def get_request_over_unix_socket(socket_path, url_path):
        # Create a connector that uses the Unix socket
        connector = aiohttp.UnixConnector(path=socket_path)

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url_path) as response:
                print(response.status)
                print(await response.text())

    await get_request_over_unix_socket('/tmp/uvicorn.sock', 'http://localhost/get_info')

def test_get_table_rows():
    args = {
        "json": True,
        "code": "eosio",
        "scope": "eosio",
        "table": "global",
        "lower_bound": "",
        "upper_bound": "",
        "limit": 10,
        "key_type": '',
        "index_position": '',
        "encode_type": 'dec',
        "reverse": False,
        "show_payer": False
    }
    url = 'http://127.0.0.1:8809/v1/chain/get_table_rows'
    url = 'http://127.0.0.1:8810/v1/chain/get_table_rows'
    url = 'http://127.0.0.1:8820/v1/chain/get_table_rows'
    for i in range(20):
        ret = requests.post(url, json=args)
        logger.info(ret.text)

def test_push_transaction():
    port = 8820
    ret = requests.get(f'http://127.0.0.1:{port}/v1/chain/get_info')
    info = json.loads(ret.text)
    logger.info(info)
    ref_block_id = info['last_irreversible_block_id']
    count = 5000
    txs = []
    for i in range(count):
        tx = SignedTransaction(int(time.time())+60*10, ref_block_id)
        tx.add_action('eosio', 'sayhello', b'hello, world' + str(i).encode(), {'eosio': 'active'})
        priv_key = PrivateKey.from_base58('5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3')
        tx.sign(priv_key, info['chain_id'])
        raw_tx = tx.pack_ex()
        packed_tx = raw_tx.hex()
        txs.append(packed_tx)
    for packed_tx in txs:
        args = {'packed_tx': packed_tx, 'speculate': False}
        ret = requests.post(f'http://127.0.0.1:{port}/v1/chain/push_transaction', json=args)
        text = ret.text
        # logger.info(text)
        # logger.info(json.loads(text))
        assert ret.status_code == 200