import json
import logging
import pytest
import requests
import time

from ipyeos import eos
from ipyeos.types import PrivateKey
from ipyeos.signed_transaction import SignedTransaction
from ipyeos.chain_exceptions import AssertException

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
