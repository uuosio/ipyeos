# Interactive Python for Eos

[![PyPi](https://img.shields.io/pypi/v/ipyeos.svg)](https://pypi.org/project/ipyeos)
[![PyPi](https://img.shields.io/pypi/dm/ipyeos.svg)](https://pypi.org/project/ipyeos)


## What Is IPyEos

- IPyEos is a Smart Contracts test framework for Eos
- IPyEos is a Python binding for Eos

## Installation

```
python3 -m pip install ipyeos
cdt-init
```

on the macOS platform, you may need to install `gmp` and `zstd` if you don't install them.

```bash
brew reinstall gmp
brew reinstall zstd
```

Also, you can install the `ipyeos` docker image with the following command if your machine does not support install `ipyeos` directly.

```bash
docker pull ghcr.io/uuosio/ipyeos:latest
```

## Building

To build this project, please follow the steps below:

1. Clone the source code from the repository:

```bash
git clone https://github.com/uuosio/ipyeos --branch main --recursive
```

2. Build the forked leap source code under the `leap` directory by following the instructions in the [build-and-install-from-source](https://github.com/uuosio/leap/tree/550e092fa980e673f5f6fe5a7c309c088441f09a#build-and-install-from-source) documentation.

3. Build the Python release package:

```bash
cd ipyeos
./build.sh
```

4. Install the Python package

```bash
python3 -m pip install dist/pyeos-0.4.0**.whl
```

## Run a Node

```bash
eosnode
```

## Run a Debugging Server

```bash
eosdebugger
```

or use the following command if you have installed `ipyeos` docker image:

```bash
docker run -it --rm -p 9090:9090 -p 9092:9092 -t ghcr.io/uuosio/ipyeos
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

# Note

If you encounter the error message during running the above commands like `Failed to load libpython3.7m.so!`, try running the following command in your terminal:

```bash
export PYTHON_SHARED_LIB_PATH=path/to/libpython[.so|.dylib]
```

# License
[MIT](./LICENSE)
