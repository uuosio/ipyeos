# Interactive Python for Eos

## What Is IPyEos

1. IPyEos is a Smart Contracts test framework for Eos
2. IPyEos is a Python binding for Eos

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
eos-node
```

## Run a Debugging Server

```
eos-debugger
```

## Testing

```
ipyeos -m pytest -x -s tests/test.py
```

## Run a Testnet

```
ipyeos -m ipyeos eos-node --data-dir dd --config-dir cd -p eosio --plugin eosio::producer_plugin --plugin eosio::chain_api_plugin --plugin eosio::producer_api_plugin --plugin eosio::history_api_plugin -e --resource-monitor-space-threshold 99 --http-server-address 127.0.0.1:8889 --contracts-console --access-control-allow-origin="*" --backing-store rocksdb --wasm-runtime eos-vm-jit
```

Also, you can run a test node with `eos-node` command directly.

```
eos-node --data-dir dd --config-dir cd -p eosio --plugin eosio::producer_plugin --plugin eosio::chain_api_plugin --plugin eosio::producer_api_plugin --plugin eosio::history_api_plugin -e --resource-monitor-space-threshold 99 --http-server-address 127.0.0.1:8889 --contracts-console --access-control-allow-origin="*" --backing-store rocksdb --wasm-runtime eos-vm-jit
```

# License
[MIT](./LICENSE)
