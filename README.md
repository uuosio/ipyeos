# Interactive Python for Eos

## What Is IPyEos

- IPyEos is a Smart Contracts test framework for Eos
- IPyEos is a Python binding for Eos

## Installation

```
python3 -m pip install ipyeos
```

## Building

```
git clone https://github.com/uuosio/ipyeos --branch main --recursive
cd eos
./build.sh
cd ..
./build.sh
```

## Run a Node

```
eosnode
```

## Run a Debugging Server

```
eosdebugger
```

## Testing

test example code

```python
#test.py
import os
from ipyeos.chaintester import ChainTester

chaintester.chain_config['contracts_console'] = True

def test_example():
    t = ChainTester(True)
    with open('./hello/build/hello/hello.wasm', 'rb') as f:
        code = f.read()
    with open('./hello/build/hello/hello.abi', 'rb') as f:
        abi = f.read()
    t.deploy_contract('hello', code, abi)
    t.produce_block()

    t.push_action('hello', 'hi', {'nm': 'alice'}, {'hello': 'active'})
    t.produce_block()
```

```
ipyeos -m pytest -x -s tests/test.py
```

## Run a Testnet

```
ipyeos -m ipyeos eosnode --data-dir dd --config-dir cd -p eosio --plugin eosio::producer_plugin --plugin eosio::chain_api_plugin --plugin eosio::producer_api_plugin --plugin eosio::history_api_plugin -e --resource-monitor-space-threshold 99 --http-server-address 127.0.0.1:8889 --contracts-console --access-control-allow-origin="*" --backing-store rocksdb --wasm-runtime eos-vm-jit
```

Also, you can run a test node with `eosnode` command directly.

```
eosnode --data-dir dd --config-dir cd -p eosio --plugin eosio::producer_plugin --plugin eosio::chain_api_plugin --plugin eosio::producer_api_plugin --plugin eosio::history_api_plugin -e --resource-monitor-space-threshold 99 --http-server-address 127.0.0.1:8889 --contracts-console --access-control-allow-origin="*" --backing-store rocksdb --wasm-runtime eos-vm-jit
```

# License
[MIT](./LICENSE)
