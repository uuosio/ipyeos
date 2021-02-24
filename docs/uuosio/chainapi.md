# ChainApi

> Auto-generated documentation for [uuosio.chainapi](../../uuosio/chainapi.py) module.

- [Extlib](../README.md#extlib-index) / [Modules](../MODULES.md#extlib-modules) / [Uuosio](index.md#uuosio) / ChainApi
    - [ChainApi](#chainapi)
        - [ChainApi().abi_bin_to_json](#chainapiabi_bin_to_json)
        - [ChainApi().abi_json_to_bin](#chainapiabi_json_to_bin)
        - [ChainApi().db_size_api_get](#chainapidb_size_api_get)
        - [ChainApi().get_abi](#chainapiget_abi)
        - [ChainApi().get_account](#chainapiget_account)
        - [ChainApi().get_activated_protocol_features](#chainapiget_activated_protocol_features)
        - [ChainApi().get_block](#chainapiget_block)
        - [ChainApi().get_block_header_state](#chainapiget_block_header_state)
        - [ChainApi().get_code](#chainapiget_code)
        - [ChainApi().get_code_hash](#chainapiget_code_hash)
        - [ChainApi().get_currency_balance](#chainapiget_currency_balance)
        - [ChainApi().get_currency_stats](#chainapiget_currency_stats)
        - [ChainApi().get_info](#chainapiget_info)
        - [ChainApi().get_producer_schedule](#chainapiget_producer_schedule)
        - [ChainApi().get_producers](#chainapiget_producers)
        - [ChainApi().get_raw_abi](#chainapiget_raw_abi)
        - [ChainApi().get_raw_code_and_abi](#chainapiget_raw_code_and_abi)
        - [ChainApi().get_required_keys](#chainapiget_required_keys)
        - [ChainApi().get_scheduled_transactions](#chainapiget_scheduled_transactions)
        - [ChainApi().get_table_by_scope](#chainapiget_table_by_scope)
        - [ChainApi().get_table_rows](#chainapiget_table_rows)
        - [ChainApi().get_table_rows](#chainapiget_table_rows)
        - [ChainApi().get_transaction_id](#chainapiget_transaction_id)
        - [ChainApi().recover_reversible_blocks](#chainapirecover_reversible_blocks)
        - [ChainApi().repair_log](#chainapirepair_log)
    - [recover_reversible_blocks](#recover_reversible_blocks)
    - [repair_log](#repair_log)

## ChainApi

[[find in source code]](../../uuosio/chainapi.py#L4)

```python
class ChainApi(object):
    def __init__(chain_ptr):
```

### ChainApi().abi_bin_to_json

[[find in source code]](../../uuosio/chainapi.py#L71)

```python
def abi_bin_to_json(params):
```

### ChainApi().abi_json_to_bin

[[find in source code]](../../uuosio/chainapi.py#L68)

```python
def abi_json_to_bin(params):
```

### ChainApi().db_size_api_get

[[find in source code]](../../uuosio/chainapi.py#L89)

```python
def db_size_api_get():
```

### ChainApi().get_abi

[[find in source code]](../../uuosio/chainapi.py#L33)

```python
def get_abi(params):
```

### ChainApi().get_account

[[find in source code]](../../uuosio/chainapi.py#L21)

```python
def get_account(name):
```

### ChainApi().get_activated_protocol_features

[[find in source code]](../../uuosio/chainapi.py#L12)

```python
def get_activated_protocol_features(params):
```

### ChainApi().get_block

[[find in source code]](../../uuosio/chainapi.py#L15)

```python
def get_block(params):
```

### ChainApi().get_block_header_state

[[find in source code]](../../uuosio/chainapi.py#L18)

```python
def get_block_header_state(params):
```

### ChainApi().get_code

[[find in source code]](../../uuosio/chainapi.py#L27)

```python
def get_code(params):
```

### ChainApi().get_code_hash

[[find in source code]](../../uuosio/chainapi.py#L30)

```python
def get_code_hash(params):
```

### ChainApi().get_currency_balance

[[find in source code]](../../uuosio/chainapi.py#L48)

```python
def get_currency_balance(params):
```

### ChainApi().get_currency_stats

[[find in source code]](../../uuosio/chainapi.py#L56)

```python
def get_currency_stats(params):
```

### ChainApi().get_info

[[find in source code]](../../uuosio/chainapi.py#L9)

```python
def get_info():
```

### ChainApi().get_producer_schedule

[[find in source code]](../../uuosio/chainapi.py#L62)

```python
def get_producer_schedule(params):
```

### ChainApi().get_producers

[[find in source code]](../../uuosio/chainapi.py#L59)

```python
def get_producers(params):
```

### ChainApi().get_raw_abi

[[find in source code]](../../uuosio/chainapi.py#L39)

```python
def get_raw_abi(params):
```

### ChainApi().get_raw_code_and_abi

[[find in source code]](../../uuosio/chainapi.py#L36)

```python
def get_raw_code_and_abi(params):
```

### ChainApi().get_required_keys

[[find in source code]](../../uuosio/chainapi.py#L74)

```python
def get_required_keys(params):
```

### ChainApi().get_scheduled_transactions

[[find in source code]](../../uuosio/chainapi.py#L65)

```python
def get_scheduled_transactions(params):
```

### ChainApi().get_table_by_scope

[[find in source code]](../../uuosio/chainapi.py#L45)

```python
def get_table_by_scope(params):
```

### ChainApi().get_table_rows

[[find in source code]](../../uuosio/chainapi.py#L42)

```python
def get_table_rows(params):
```

### ChainApi().get_table_rows

[[find in source code]](../../uuosio/chainapi.py#L86)

```python
def get_table_rows(params):
```

### ChainApi().get_transaction_id

[[find in source code]](../../uuosio/chainapi.py#L77)

```python
def get_transaction_id(params):
```

### ChainApi().recover_reversible_blocks

[[find in source code]](../../uuosio/chainapi.py#L80)

```python
def recover_reversible_blocks(
    old_reversible_blocks_dir,
    new_reversible_blocks_dir,
    reversible_cache_size=340 * 1024 * 1024,
    truncate_at_block=0,
):
```

### ChainApi().repair_log

[[find in source code]](../../uuosio/chainapi.py#L83)

```python
def repair_log(blocks_dir, truncate_at_block=0):
```

## recover_reversible_blocks

[[find in source code]](../../uuosio/chainapi.py#L95)

```python
def recover_reversible_blocks(
    old_reversible_blocks_dir,
    new_reversible_blocks_dir,
    reversible_cache_size=340 * 1024 * 1024,
    truncate_at_block=0,
):
```

## repair_log

[[find in source code]](../../uuosio/chainapi.py#L92)

```python
def repair_log(blocks_dir, truncate_at_block=0):
```
