# Interactive Python for Eos

[![PyPi](https://img.shields.io/pypi/v/ipyeos.svg)](https://pypi.org/project/ipyeos)
[![PyPi](https://img.shields.io/pypi/dm/ipyeos.svg)](https://pypi.org/project/ipyeos)


## What Is IPyEos

- IPyEos is a Smart Contracts test framework for Eos
- IPyEos is a Python binding for Eos

## Installation

```
python3 -m pip install ipyeos
```

on the macOS platform, you may need to install `gmp` and `zstd` if you don't install them.

```bash
brew reinstall gmp
brew reinstall zstd
```

If your platform is Windows or MacOSX M1/M2, you also need to download an image that includes the ipyeos tool:

```bash
docker pull ghcr.io/uuosio/ipyeos:latest
```

If you have not installed the ipyeos image in Docker, then the ipyeos image will be automatically downloaded the first time you run `ipyeos` or `eosdebugger`.

On macOS, the recommended software for installing and running Docker is [OrbStack](https://orbstack.dev/download). For other platforms, you can use [Docker Desktop](https://www.docker.com/products/docker-desktop).

## Test Examples


### Example 1:

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

Test:

```
ipyeos -m pytest -x -s tests/test.py
```

### Restore from snapshot Example

```python
def test_snapshot():
    # data_name = './data'
    # snapshot_dir = './snapshot-2023-06-18-01-eos-v6-0315729695.bin'
    # state_size = 32*1024*1024*1024
    if os.path.exists('./data/ddd'):
        shutil.rmtree('./data/ddd')
    state_size = 10*1024*1024
    data_name = './data'
    snapshot_dir = './data/snapshot-0000001ba25b3b5af4ba6cacecb68ef4238a50bb7134e56fe985b4355fbf7488.bin'

    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_dir=snapshot_dir)
```

### Accessing Database Object Example

```python
def test_database_object():
    # data_name = './data'
    # snapshot_dir = './snapshot-2023-06-18-01-eos-v6-0315729695.bin'
    # state_size = 32*1024*1024*1024
    if os.path.exists('./data/ddd'):
        shutil.rmtree('./data/ddd')
    state_size = 10*1024*1024
    data_name = './data'
    snapshot_dir = './data/snapshot-0000001ba25b3b5af4ba6cacecb68ef4238a50bb7134e56fe985b4355fbf7488.bin'

    # {'private': '5K3x5DPEbocfZSG8XD3RiyJAfPFH5Bd9ED15wtdEMbqzXCLPbma',
    #  'public': 'EOS5K93aPtTdov2zWDqYxVcMQ4GBT1hyEpED8tjzPuLsf31tPySNY'}

    # must call set_debug_producer_key and import_producer_key before create ChainTester
    eos.set_debug_producer_key('EOS5K93aPtTdov2zWDqYxVcMQ4GBT1hyEpED8tjzPuLsf31tPySNY')
    chaintester.import_producer_key('5K3x5DPEbocfZSG8XD3RiyJAfPFH5Bd9ED15wtdEMbqzXCLPbma')

    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_dir=snapshot_dir)
    logger.info("+++++producer keys: %s", t.chain.get_producer_public_keys())
    t.produce_block()
    logger.info("+++++++%s", t.api.get_info())

    idx = PermissionObjectIndex(t.db)
    perm = idx.find_by_owner('eosio.token', 'active')
    print(perm)

    # Private key: 5JBW9jddvqHY7inGEK2qWbGLYKeqm32NDYL3fLdYgMjnWxRjXLF
    # Public key: EOS6hM1U89jbHWyX8ArHttFzoGe21y7ehXvtN5q7GbDxYEa9NFXH2
    t.import_key('5JBW9jddvqHY7inGEK2qWbGLYKeqm32NDYL3fLdYgMjnWxRjXLF')
    keys = [KeyWeight(PublicKey.from_base58('EOS6hM1U89jbHWyX8ArHttFzoGe21y7ehXvtN5q7GbDxYEa9NFXH2'), 1)]
    perm.auth = Authority(1, keys, [], [])

    ret = idx.modify(perm)
    print('modify_by_id return:', ret)

    idx = PermissionObjectIndex(t.db)
    perm = idx.find_by_owner('eosio.token', 'active')
    print(perm)
```

### Push Block Example:

```python
def test_push_block():
    if os.path.exists('./data/ddd'):
        shutil.rmtree('./data/ddd')

    state_size = 10*1024*1024
    data_name = './data'

    snapshot_dir = './data/push_block/snapshot-0000003b83662343c208e965654f4d906ed7fad0372e13c246981cd076d379bb.bin'
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_dir=snapshot_dir)
    t.free()

    snapshot_dir = ''
    t = ChainTester(True, data_dir=os.path.join(data_name, 'ddd'), config_dir=os.path.join(data_name, 'cd'), state_size=state_size, snapshot_dir=snapshot_dir)
    t.chain.abort_block()

    info = t.api.get_info()
    head_block_num = info['head_block_num']
    log = BlockLog('./data/push_block/blocks')
    logger.info("%s %s", head_block_num, log.head_block_num())
    num_count = log.head_block_num() - head_block_num

    for block_num in range(head_block_num+1, head_block_num+num_count+1):
        t.chain.push_block(log, block_num)

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
python3 -m pip install dist/pyeos-0.4.7**.whl
```

## Run a Node

```bash
eosnode
```

## Run a Debugging Server

```bash
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

```bash
ipyeos -m ipyeos eosnode --data-dir dd --config-dir cd -p eosio --plugin eosio::producer_plugin --plugin eosio::chain_api_plugin --plugin eosio::producer_api_plugin -e --resource-monitor-space-threshold 99 --http-server-address 127.0.0.1:8889 --contracts-console --access-control-allow-origin="*"  --wasm-runtime eos-vm-jit
```

Also, you can run a test node with `eosnode` command directly.

```bash
eosnode --data-dir dd --config-dir cd -p eosio --plugin eosio::producer_plugin --plugin eosio::chain_api_plugin --plugin eosio::producer_api_plugin -e --resource-monitor-space-threshold 99 --http-server-address 127.0.0.1:8889 --contracts-console --access-control-allow-origin="*"  --wasm-runtime eos-vm-jit
```

# Note

If you encounter the error message during running the above commands like `Failed to load libpython3.7m.so!`, try running the following command in your terminal:

```bash
export PYTHON_SHARED_LIB_PATH=path/to/libpython[.so|.dylib]
```

# License
[MIT](./LICENSE)
