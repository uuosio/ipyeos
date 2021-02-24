# ChainTest

> Auto-generated documentation for [uuosio.chaintest](../../uuosio/chaintest.py) module.

- [Extlib](../README.md#extlib-index) / [Modules](../MODULES.md#extlib-modules) / [Uuosio](index.md#uuosio) / ChainTest
    - [ChainTest](#chaintest)
        - [ChainTest().buy_ram_bytes](#chaintestbuy_ram_bytes)
        - [ChainTest().calc_pending_block_time](#chaintestcalc_pending_block_time)
        - [ChainTest().chain](#chaintestchain)
        - [ChainTest().chain](#chaintestchain)
        - [ChainTest().compile_py_code](#chaintestcompile_py_code)
        - [ChainTest().compile_py_code_from_file](#chaintestcompile_py_code_from_file)
        - [ChainTest().create_account](#chaintestcreate_account)
        - [ChainTest().db_test1](#chaintestdb_test1)
        - [ChainTest().db_test2](#chaintestdb_test2)
        - [ChainTest().db_test3](#chaintestdb_test3)
        - [ChainTest().delegatebw](#chaintestdelegatebw)
        - [ChainTest().deploy_contract](#chaintestdeploy_contract)
        - [ChainTest().deploy_eosio_bios](#chaintestdeploy_eosio_bios)
        - [ChainTest().deploy_eosio_system](#chaintestdeploy_eosio_system)
        - [ChainTest().deploy_eosio_system_uuos](#chaintestdeploy_eosio_system_uuos)
        - [ChainTest().deploy_eosio_system_uuos_test](#chaintestdeploy_eosio_system_uuos_test)
        - [ChainTest().deploy_eosio_token](#chaintestdeploy_eosio_token)
        - [ChainTest().deploy_python_contract](#chaintestdeploy_python_contract)
        - [ChainTest().find_private_key](#chaintestfind_private_key)
        - [ChainTest().free](#chaintestfree)
        - [ChainTest().gen_action](#chaintestgen_action)
        - [ChainTest().gen_trx](#chaintestgen_trx)
        - [ChainTest().get_account](#chaintestget_account)
        - [ChainTest().get_balance](#chaintestget_balance)
        - [ChainTest().get_info](#chaintestget_info)
        - [ChainTest().get_scheduled_transactions](#chaintestget_scheduled_transactions)
        - [ChainTest().get_table_rows](#chaintestget_table_rows)
        - [ChainTest().init](#chaintestinit)
        - [ChainTest().on_accepted_block](#chainteston_accepted_block)
        - [ChainTest().pack_args](#chaintestpack_args)
        - [ChainTest().produce_block](#chaintestproduce_block)
        - [ChainTest().push_action](#chaintestpush_action)
        - [ChainTest().push_action_with_multiple_permissions](#chaintestpush_action_with_multiple_permissions)
        - [ChainTest().push_actions](#chaintestpush_actions)
        - [ChainTest().s2b](#chaintests2b)
        - [ChainTest().start_block](#chainteststart_block)
        - [ChainTest().start_block_test](#chainteststart_block_test)
        - [ChainTest().test1](#chaintesttest1)
        - [ChainTest().test2](#chaintesttest2)
        - [ChainTest().test3](#chaintesttest3)
        - [ChainTest().test4](#chaintesttest4)
        - [ChainTest().test5](#chaintesttest5)
        - [ChainTest().test6](#chaintesttest6)
        - [ChainTest().test7](#chaintesttest7)
        - [ChainTest().test_create_account](#chaintesttest_create_account)
        - [ChainTest().test_create_account_uuos](#chaintesttest_create_account_uuos)
        - [ChainTest().test_jit](#chaintesttest_jit)
        - [ChainTest().test_set_action_return_value](#chaintesttest_set_action_return_value)
        - [ChainTest().transfer](#chaintesttransfer)
        - [ChainTest().unpack_args](#chaintestunpack_args)
        - [ChainTest().update_auth](#chaintestupdate_auth)
    - [Object](#object)
    - [isoformat](#isoformat)

## ChainTest

[[find in source code]](../../uuosio/chaintest.py#L154)

```python
class ChainTest(object):
    def __init__(network_type=2, jit=True, data_dir=None, config_dir=None):
```

### ChainTest().buy_ram_bytes

[[find in source code]](../../uuosio/chaintest.py#L624)

```python
def buy_ram_bytes(payer, receiver, _bytes):
```

### ChainTest().calc_pending_block_time

[[find in source code]](../../uuosio/chaintest.py#L405)

```python
def calc_pending_block_time():
```

### ChainTest().chain

[[find in source code]](../../uuosio/chaintest.py#L365)

```python
@property
def chain():
```

### ChainTest().chain

[[find in source code]](../../uuosio/chaintest.py#L369)

```python
@chain.setter
def chain(c):
```

### ChainTest().compile_py_code

[[find in source code]](../../uuosio/chaintest.py#L1040)

```python
def compile_py_code(code):
```

### ChainTest().compile_py_code_from_file

[[find in source code]](../../uuosio/chaintest.py#L1032)

```python
def compile_py_code_from_file(code_file):
```

### ChainTest().create_account

[[find in source code]](../../uuosio/chaintest.py#L578)

```python
def create_account(
    creator,
    account,
    owner_key,
    active_key,
    ram_bytes=0,
    stake_net=0.0,
    stake_cpu=0.0,
):
```

### ChainTest().db_test1

[[find in source code]](../../uuosio/chaintest.py#L1045)

```python
def db_test1():
```

### ChainTest().db_test2

[[find in source code]](../../uuosio/chaintest.py#L1053)

```python
def db_test2():
```

### ChainTest().db_test3

[[find in source code]](../../uuosio/chaintest.py#L1067)

```python
def db_test3():
```

### ChainTest().delegatebw

[[find in source code]](../../uuosio/chaintest.py#L629)

```python
def delegatebw(_from, receiver, stake_net, stake_cpu, transfer=0):
```

### ChainTest().deploy_contract

[[find in source code]](../../uuosio/chaintest.py#L641)

```python
def deploy_contract(account, code, abi, vm_type=0, show_elapse=True):
```

### ChainTest().deploy_eosio_bios

[[find in source code]](../../uuosio/chaintest.py#L792)

```python
def deploy_eosio_bios():
```

### ChainTest().deploy_eosio_system

[[find in source code]](../../uuosio/chaintest.py#L783)

```python
def deploy_eosio_system():
```

### ChainTest().deploy_eosio_system_uuos

[[find in source code]](../../uuosio/chaintest.py#L750)

```python
def deploy_eosio_system_uuos():
```

### ChainTest().deploy_eosio_system_uuos_test

[[find in source code]](../../uuosio/chaintest.py#L773)

```python
def deploy_eosio_system_uuos_test():
```

### ChainTest().deploy_eosio_token

[[find in source code]](../../uuosio/chaintest.py#L738)

```python
def deploy_eosio_token():
```

### ChainTest().deploy_python_contract

[[find in source code]](../../uuosio/chaintest.py#L680)

```python
def deploy_python_contract(account, code, abi):
```

### ChainTest().find_private_key

[[find in source code]](../../uuosio/chaintest.py#L497)

```python
def find_private_key(actor, perm_name):
```

### ChainTest().free

[[find in source code]](../../uuosio/chaintest.py#L1124)

```python
def free():
```

### ChainTest().gen_action

[[find in source code]](../../uuosio/chaintest.py#L427)

```python
def gen_action(account, action, args, permissions={}):
```

### ChainTest().gen_trx

[[find in source code]](../../uuosio/chaintest.py#L804)

```python
def gen_trx():
```

### ChainTest().get_account

[[find in source code]](../../uuosio/chaintest.py#L878)

```python
def get_account(account):
```

### ChainTest().get_balance

[[find in source code]](../../uuosio/chaintest.py#L378)

```python
def get_balance(account, token_account='uuos.token', token_name='UUOS'):
```

### ChainTest().get_info

[[find in source code]](../../uuosio/chaintest.py#L875)

```python
def get_info():
```

### ChainTest().get_scheduled_transactions

[[find in source code]](../../uuosio/chaintest.py#L856)

```python
def get_scheduled_transactions():
```

### ChainTest().get_table_rows

[[find in source code]](../../uuosio/chaintest.py#L1130)

```python
def get_table_rows(
    _json,
    code,
    scope,
    table,
    lower_bound,
    upper_bound,
    limit,
    encode_type='dec',
) -> dict:
```

Fetch smart contract data from an account.

### ChainTest().init

[[find in source code]](../../uuosio/chaintest.py#L254)

```python
def init():
```

### ChainTest().on_accepted_block

[[find in source code]](../../uuosio/chaintest.py#L373)

```python
def on_accepted_block(block, num, block_id):
```

### ChainTest().pack_args

[[find in source code]](../../uuosio/chaintest.py#L566)

```python
def pack_args(account, action, args):
```

### ChainTest().produce_block

[[find in source code]](../../uuosio/chaintest.py#L859)

```python
def produce_block():
```

### ChainTest().push_action

[[find in source code]](../../uuosio/chaintest.py#L445)

```python
def push_action(account, action, args, permissions={}):
```

### ChainTest().push_action_with_multiple_permissions

[[find in source code]](../../uuosio/chaintest.py#L473)

```python
def push_action_with_multiple_permissions(account, action, args, permissions):
```

### ChainTest().push_actions

[[find in source code]](../../uuosio/chaintest.py#L516)

```python
def push_actions(actions):
```

### ChainTest().s2b

[[find in source code]](../../uuosio/chaintest.py#L676)

```python
def s2b(s):
```

### ChainTest().start_block

[[find in source code]](../../uuosio/chaintest.py#L849)

```python
def start_block():
```

### ChainTest().start_block_test

[[find in source code]](../../uuosio/chaintest.py#L834)

```python
def start_block_test():
```

### ChainTest().test1

[[find in source code]](../../uuosio/chaintest.py#L906)

```python
def test1():
```

### ChainTest().test2

[[find in source code]](../../uuosio/chaintest.py#L927)

```python
def test2():
```

### ChainTest().test3

[[find in source code]](../../uuosio/chaintest.py#L930)

```python
def test3():
```

### ChainTest().test4

[[find in source code]](../../uuosio/chaintest.py#L955)

```python
def test4():
```

### ChainTest().test5

[[find in source code]](../../uuosio/chaintest.py#L981)

```python
def test5():
```

### ChainTest().test6

[[find in source code]](../../uuosio/chaintest.py#L1001)

```python
def test6():
```

### ChainTest().test7

[[find in source code]](../../uuosio/chaintest.py#L1024)

```python
def test7():
```

### ChainTest().test_create_account

[[find in source code]](../../uuosio/chaintest.py#L896)

```python
def test_create_account():
```

### ChainTest().test_create_account_uuos

[[find in source code]](../../uuosio/chaintest.py#L886)

```python
def test_create_account_uuos():
```

### ChainTest().test_jit

[[find in source code]](../../uuosio/chaintest.py#L1100)

```python
def test_jit():
```

### ChainTest().test_set_action_return_value

[[find in source code]](../../uuosio/chaintest.py#L1086)

```python
def test_set_action_return_value():
```

### ChainTest().transfer

[[find in source code]](../../uuosio/chaintest.py#L560)

```python
def transfer(
    _from,
    _to,
    _amount,
    _memo='',
    token_account='uuos.token',
    token_name='',
    permission='active',
):
```

### ChainTest().unpack_args

[[find in source code]](../../uuosio/chaintest.py#L572)

```python
def unpack_args(account, action, raw_args):
```

### ChainTest().update_auth

[[find in source code]](../../uuosio/chaintest.py#L723)

```python
def update_auth(account, accounts, keys, perm='active', parent='owner'):
```

## Object

[[find in source code]](../../uuosio/chaintest.py#L108)

```python
class Object():
```

## isoformat

[[find in source code]](../../uuosio/chaintest.py#L31)

```python
def isoformat(dt):
```
