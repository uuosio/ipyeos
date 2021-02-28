# Building

```
git clone https://github.com/uuosio/uuos --branch main --recursive
cd uuos
python3.7 -m pip install -r requirements.txt
./scripts/build.sh
```

# Installation

```
./scripts/install_eosio.sh
```

# Testing

```
run-uuos -m pytest -x -s pysrc/tests/test_micropython.py -k test_hello
```

# Run a Testnet

```
run-uuos -m uuosio.main --data-dir dd --config-dir cd -p eosio --plugin eosio::producer_plugin --plugin eosio::chain_api_plugin --plugin eosio::producer_api_plugin --plugin eosio::history_api_plugin -e --resource-monitor-space-threshold 99 --http-server-address 127.0.0.1:8889 --block-interval-ms 1000 --contracts-console --access-control-allow-origin="*" --backing-store rocksdb --wasm-runtime eos-vm-jit
```

# License
[MIT](./LICENSE)
