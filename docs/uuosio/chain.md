# Chain

> Auto-generated documentation for [uuosio.chain](../../uuosio/chain.py) module.

- [Extlib](../README.md#extlib-index) / [Modules](../MODULES.md#extlib-modules) / [Uuosio](index.md#uuosio) / Chain
    - [Chain](#chain)
        - [Chain().abort_block](#chainabort_block)
        - [Chain().active_producers](#chainactive_producers)
        - [Chain().add_resource_greylist](#chainadd_resource_greylist)
        - [Chain().add_to_ram_correction](#chainadd_to_ram_correction)
        - [Chain().all_subjective_mitigations_disabled](#chainall_subjective_mitigations_disabled)
        - [Chain().calculate_integrity_hash](#chaincalculate_integrity_hash)
        - [Chain().check_action_list](#chaincheck_action_list)
        - [Chain().check_actor_list](#chaincheck_actor_list)
        - [Chain().check_contract_list](#chaincheck_contract_list)
        - [Chain().check_key_list](#chaincheck_key_list)
        - [Chain().commit_block](#chaincommit_block)
        - [Chain().contracts_console](#chaincontracts_console)
        - [Chain().fetch_block_by_id](#chainfetch_block_by_id)
        - [Chain().fetch_block_by_number](#chainfetch_block_by_number)
        - [Chain().fetch_block_by_number](#chainfetch_block_by_number)
        - [Chain().fetch_block_state_by_id](#chainfetch_block_state_by_id)
        - [Chain().fetch_block_state_by_number](#chainfetch_block_state_by_number)
        - [Chain().finalize_block](#chainfinalize_block)
        - [Chain().fork_db_head_block_id](#chainfork_db_head_block_id)
        - [Chain().fork_db_head_block_num](#chainfork_db_head_block_num)
        - [Chain().fork_db_head_block_producer](#chainfork_db_head_block_producer)
        - [Chain().fork_db_head_block_time](#chainfork_db_head_block_time)
        - [Chain().fork_db_pending_head_block_id](#chainfork_db_pending_head_block_id)
        - [Chain().fork_db_pending_head_block_num](#chainfork_db_pending_head_block_num)
        - [Chain().fork_db_pending_head_block_num](#chainfork_db_pending_head_block_num)
        - [Chain().fork_db_pending_head_block_producer](#chainfork_db_pending_head_block_producer)
        - [Chain().fork_db_pending_head_block_time](#chainfork_db_pending_head_block_time)
        - [Chain().free](#chainfree)
        - [Chain().gen_transaction](#chaingen_transaction)
        - [Chain().get_account](#chainget_account)
        - [Chain().get_action_blacklist](#chainget_action_blacklist)
        - [Chain().get_actor_blacklist](#chainget_actor_blacklist)
        - [Chain().get_actor_whitelist](#chainget_actor_whitelist)
        - [Chain().get_block_id_for_num](#chainget_block_id_for_num)
        - [Chain().get_block_id_for_num](#chainget_block_id_for_num)
        - [Chain().get_config](#chainget_config)
        - [Chain().get_contract_blacklist](#chainget_contract_blacklist)
        - [Chain().get_contract_whitelist](#chainget_contract_whitelist)
        - [Chain().get_dynamic_global_properties](#chainget_dynamic_global_properties)
        - [Chain().get_global_properties](#chainget_global_properties)
        - [Chain().get_greylist_limit](#chainget_greylist_limit)
        - [Chain().get_key_blacklist](#chainget_key_blacklist)
        - [Chain().get_key_blacklist](#chainget_key_blacklist)
        - [Chain().get_pending_trx_receipts](#chainget_pending_trx_receipts)
        - [Chain().get_producer_public_keys](#chainget_producer_public_keys)
        - [Chain().get_read_mode](#chainget_read_mode)
        - [Chain().get_resource_greylist](#chainget_resource_greylist)
        - [Chain().get_scheduled_producer](#chainget_scheduled_producer)
        - [Chain().get_scheduled_producer](#chainget_scheduled_producer)
        - [Chain().get_scheduled_transaction](#chainget_scheduled_transaction)
        - [Chain().get_scheduled_transactions](#chainget_scheduled_transactions)
        - [Chain().get_unapplied_transactions](#chainget_unapplied_transactions)
        - [Chain().get_validation_mode](#chainget_validation_mode)
        - [Chain().head_block_header](#chainhead_block_header)
        - [Chain().head_block_id](#chainhead_block_id)
        - [Chain().head_block_num](#chainhead_block_num)
        - [Chain().head_block_producer](#chainhead_block_producer)
        - [Chain().head_block_state](#chainhead_block_state)
        - [Chain().head_block_time](#chainhead_block_time)
        - [Chain().id](#chainid)
        - [Chain().id](#chainid)
        - [Chain().is_building_block](#chainis_building_block)
        - [Chain().is_building_block](#chainis_building_block)
        - [Chain().is_builtin_activated](#chainis_builtin_activated)
        - [Chain().is_known_unexpired_transaction](#chainis_known_unexpired_transaction)
        - [Chain().is_producing_block](#chainis_producing_block)
        - [Chain().is_protocol_feature_activated](#chainis_protocol_feature_activated)
        - [Chain().is_ram_billing_in_notify_allowed](#chainis_ram_billing_in_notify_allowed)
        - [Chain().is_resource_greylisted](#chainis_resource_greylisted)
        - [Chain().is_uuos_mainnet](#chainis_uuos_mainnet)
        - [Chain().last_irreversible_block_id](#chainlast_irreversible_block_id)
        - [Chain().last_irreversible_block_num](#chainlast_irreversible_block_num)
        - [Chain().light_validation_allowed](#chainlight_validation_allowed)
        - [Chain().new](#chainnew)
        - [Chain().pack_action_args](#chainpack_action_args)
        - [Chain().pending_block_producer](#chainpending_block_producer)
        - [Chain().pending_block_signing_key](#chainpending_block_signing_key)
        - [Chain().pending_block_time](#chainpending_block_time)
        - [Chain().pending_producer_block_id](#chainpending_producer_block_id)
        - [Chain().pending_producers](#chainpending_producers)
        - [Chain().pop_block](#chainpop_block)
        - [Chain().proposed_producers](#chainproposed_producers)
        - [Chain().push_scheduled_transaction](#chainpush_scheduled_transaction)
        - [Chain().push_transaction](#chainpush_transaction)
        - [Chain().remove_resource_greylist](#chainremove_resource_greylist)
        - [Chain().sender_avoids_whitelist_blacklist_enforcement](#chainsender_avoids_whitelist_blacklist_enforcement)
        - [Chain().set_action_blacklist](#chainset_action_blacklist)
        - [Chain().set_actor_blacklist](#chainset_actor_blacklist)
        - [Chain().set_actor_whitelist](#chainset_actor_whitelist)
        - [Chain().set_contract_whitelist](#chainset_contract_whitelist)
        - [Chain().set_greylist_limit](#chainset_greylist_limit)
        - [Chain().set_key_blacklist](#chainset_key_blacklist)
        - [Chain().set_proposed_producers](#chainset_proposed_producers)
        - [Chain().set_subjective_cpu_leeway](#chainset_subjective_cpu_leeway)
        - [Chain().skip_auth_check](#chainskip_auth_check)
        - [Chain().skip_db_sessions](#chainskip_db_sessions)
        - [Chain().skip_trx_checks](#chainskip_trx_checks)
        - [Chain().start_block](#chainstart_block)
        - [Chain().startup](#chainstartup)
        - [Chain().unpack_action_args](#chainunpack_action_args)
        - [Chain().validate_db_available_size](#chainvalidate_db_available_size)
        - [Chain().validate_expiration](#chainvalidate_expiration)
        - [Chain().validate_reversible_available_size](#chainvalidate_reversible_available_size)
        - [Chain().validate_tapos](#chainvalidate_tapos)

## Chain

[[find in source code]](../../uuosio/chain.py#L6)

```python
class Chain(object):
    def __init__(config, genesis, protocol_features_dir, snapshot_dir):
```

### Chain().abort_block

[[find in source code]](../../uuosio/chain.py#L38)

```python
def abort_block():
```

### Chain().active_producers

[[find in source code]](../../uuosio/chain.py#L183)

```python
def active_producers(json=True):
```

### Chain().add_resource_greylist

[[find in source code]](../../uuosio/chain.py#L249)

```python
def add_resource_greylist(name):
```

### Chain().add_to_ram_correction

[[find in source code]](../../uuosio/chain.py#L327)

```python
def add_to_ram_correction(account, ram_bytes):
```

### Chain().all_subjective_mitigations_disabled

[[find in source code]](../../uuosio/chain.py#L330)

```python
def all_subjective_mitigations_disabled():
```

### Chain().calculate_integrity_hash

[[find in source code]](../../uuosio/chain.py#L222)

```python
def calculate_integrity_hash():
```

### Chain().check_action_list

[[find in source code]](../../uuosio/chain.py#L234)

```python
def check_action_list(code, action):
```

### Chain().check_actor_list

[[find in source code]](../../uuosio/chain.py#L228)

```python
def check_actor_list(actors):
```

### Chain().check_contract_list

[[find in source code]](../../uuosio/chain.py#L231)

```python
def check_contract_list(code):
```

### Chain().check_key_list

[[find in source code]](../../uuosio/chain.py#L237)

```python
def check_key_list(pub_key):
```

### Chain().commit_block

[[find in source code]](../../uuosio/chain.py#L368)

```python
def commit_block():
```

### Chain().contracts_console

[[find in source code]](../../uuosio/chain.py#L303)

```python
def contracts_console():
```

### Chain().fetch_block_by_id

[[find in source code]](../../uuosio/chain.py#L210)

```python
def fetch_block_by_id(block_id):
```

### Chain().fetch_block_by_number

[[find in source code]](../../uuosio/chain.py#L207)

```python
def fetch_block_by_number(block_num):
```

### Chain().fetch_block_by_number

[[find in source code]](../../uuosio/chain.py#L339)

```python
def fetch_block_by_number(block_num):
```

### Chain().fetch_block_state_by_id

[[find in source code]](../../uuosio/chain.py#L216)

```python
def fetch_block_state_by_id(block_id):
```

### Chain().fetch_block_state_by_number

[[find in source code]](../../uuosio/chain.py#L213)

```python
def fetch_block_state_by_number(block_num):
```

### Chain().finalize_block

[[find in source code]](../../uuosio/chain.py#L385)

```python
def finalize_block(priv_keys):
```

### Chain().fork_db_head_block_id

[[find in source code]](../../uuosio/chain.py#L143)

```python
def fork_db_head_block_id():
```

### Chain().fork_db_head_block_num

[[find in source code]](../../uuosio/chain.py#L140)

```python
def fork_db_head_block_num():
```

### Chain().fork_db_head_block_producer

[[find in source code]](../../uuosio/chain.py#L149)

```python
def fork_db_head_block_producer():
```

### Chain().fork_db_head_block_time

[[find in source code]](../../uuosio/chain.py#L146)

```python
def fork_db_head_block_time():
```

### Chain().fork_db_pending_head_block_id

[[find in source code]](../../uuosio/chain.py#L155)

```python
def fork_db_pending_head_block_id():
```

### Chain().fork_db_pending_head_block_num

[[find in source code]](../../uuosio/chain.py#L152)

```python
def fork_db_pending_head_block_num():
```

### Chain().fork_db_pending_head_block_num

[[find in source code]](../../uuosio/chain.py#L333)

```python
def fork_db_pending_head_block_num():
```

### Chain().fork_db_pending_head_block_producer

[[find in source code]](../../uuosio/chain.py#L161)

```python
def fork_db_pending_head_block_producer():
```

### Chain().fork_db_pending_head_block_time

[[find in source code]](../../uuosio/chain.py#L158)

```python
def fork_db_pending_head_block_time():
```

### Chain().free

[[find in source code]](../../uuosio/chain.py#L21)

```python
def free():
```

### Chain().gen_transaction

[[find in source code]](../../uuosio/chain.py#L402)

```python
def gen_transaction(
    _actions,
    expiration,
    reference_block_id,
    _id,
    compress,
    _private_keys,
):
```

### Chain().get_account

[[find in source code]](../../uuosio/chain.py#L374)

```python
def get_account(account):
```

### Chain().get_action_blacklist

[[find in source code]](../../uuosio/chain.py#L77)

```python
def get_action_blacklist(json=True):
```

### Chain().get_actor_blacklist

[[find in source code]](../../uuosio/chain.py#L59)

```python
def get_actor_blacklist(json=True):
```

### Chain().get_actor_whitelist

[[find in source code]](../../uuosio/chain.py#L53)

```python
def get_actor_whitelist(json=True):
```

### Chain().get_block_id_for_num

[[find in source code]](../../uuosio/chain.py#L219)

```python
def get_block_id_for_num(block_num):
```

### Chain().get_block_id_for_num

[[find in source code]](../../uuosio/chain.py#L336)

```python
def get_block_id_for_num(num):
```

### Chain().get_config

[[find in source code]](../../uuosio/chain.py#L261)

```python
def get_config(json=True):
```

### Chain().get_contract_blacklist

[[find in source code]](../../uuosio/chain.py#L71)

```python
def get_contract_blacklist(json=True):
```

### Chain().get_contract_whitelist

[[find in source code]](../../uuosio/chain.py#L65)

```python
def get_contract_whitelist(json=True):
```

### Chain().get_dynamic_global_properties

[[find in source code]](../../uuosio/chain.py#L47)

```python
def get_dynamic_global_properties(json=True):
```

### Chain().get_global_properties

[[find in source code]](../../uuosio/chain.py#L41)

```python
def get_global_properties(json=True):
```

### Chain().get_greylist_limit

[[find in source code]](../../uuosio/chain.py#L324)

```python
def get_greylist_limit():
```

### Chain().get_key_blacklist

[[find in source code]](../../uuosio/chain.py#L83)

```python
def get_key_blacklist(json=True):
```

### Chain().get_key_blacklist

[[find in source code]](../../uuosio/chain.py#L89)

```python
def get_key_blacklist(json=True):
```

### Chain().get_pending_trx_receipts

[[find in source code]](../../uuosio/chain.py#L177)

```python
def get_pending_trx_receipts(json=True):
```

### Chain().get_producer_public_keys

[[find in source code]](../../uuosio/chain.py#L390)

```python
def get_producer_public_keys():
```

### Chain().get_read_mode

[[find in source code]](../../uuosio/chain.py#L312)

```python
def get_read_mode():
```

### Chain().get_resource_greylist

[[find in source code]](../../uuosio/chain.py#L258)

```python
def get_resource_greylist():
```

### Chain().get_scheduled_producer

[[find in source code]](../../uuosio/chain.py#L377)

```python
def get_scheduled_producer(block_time):
```

### Chain().get_scheduled_producer

[[find in source code]](../../uuosio/chain.py#L380)

```python
def get_scheduled_producer(block_time):
```

### Chain().get_scheduled_transaction

[[find in source code]](../../uuosio/chain.py#L356)

```python
def get_scheduled_transaction(sender_id, sender):
```

### Chain().get_scheduled_transactions

[[find in source code]](../../uuosio/chain.py#L361)

```python
def get_scheduled_transactions():
```

### Chain().get_unapplied_transactions

[[find in source code]](../../uuosio/chain.py#L346)

```python
def get_unapplied_transactions():
```

### Chain().get_validation_mode

[[find in source code]](../../uuosio/chain.py#L315)

```python
def get_validation_mode():
```

### Chain().head_block_header

[[find in source code]](../../uuosio/chain.py#L128)

```python
def head_block_header(json=True):
```

### Chain().head_block_id

[[find in source code]](../../uuosio/chain.py#L122)

```python
def head_block_id():
```

### Chain().head_block_num

[[find in source code]](../../uuosio/chain.py#L115)

```python
def head_block_num():
```

### Chain().head_block_producer

[[find in source code]](../../uuosio/chain.py#L125)

```python
def head_block_producer():
```

### Chain().head_block_state

[[find in source code]](../../uuosio/chain.py#L134)

```python
def head_block_state(json=True):
```

### Chain().head_block_time

[[find in source code]](../../uuosio/chain.py#L118)

```python
def head_block_time():
```

### Chain().id

[[find in source code]](../../uuosio/chain.py#L27)

```python
def id():
```

### Chain().id

[[find in source code]](../../uuosio/chain.py#L309)

```python
def id():
```

### Chain().is_building_block

[[find in source code]](../../uuosio/chain.py#L240)

```python
def is_building_block():
```

### Chain().is_building_block

[[find in source code]](../../uuosio/chain.py#L342)

```python
def is_building_block():
```

### Chain().is_builtin_activated

[[find in source code]](../../uuosio/chain.py#L282)

```python
def is_builtin_activated(feature):
```

### Chain().is_known_unexpired_transaction

[[find in source code]](../../uuosio/chain.py#L285)

```python
def is_known_unexpired_transaction(trx):
```

### Chain().is_producing_block

[[find in source code]](../../uuosio/chain.py#L243)

```python
def is_producing_block():
```

### Chain().is_protocol_feature_activated

[[find in source code]](../../uuosio/chain.py#L279)

```python
def is_protocol_feature_activated(digest):
```

### Chain().is_ram_billing_in_notify_allowed

[[find in source code]](../../uuosio/chain.py#L246)

```python
def is_ram_billing_in_notify_allowed():
```

### Chain().is_resource_greylisted

[[find in source code]](../../uuosio/chain.py#L255)

```python
def is_resource_greylisted(name):
```

### Chain().is_uuos_mainnet

[[find in source code]](../../uuosio/chain.py#L306)

```python
def is_uuos_mainnet():
```

### Chain().last_irreversible_block_id

[[find in source code]](../../uuosio/chain.py#L204)

```python
def last_irreversible_block_id():
```

### Chain().last_irreversible_block_num

[[find in source code]](../../uuosio/chain.py#L201)

```python
def last_irreversible_block_num():
```

### Chain().light_validation_allowed

[[find in source code]](../../uuosio/chain.py#L291)

```python
def light_validation_allowed(replay_opts_disabled_by_policy):
```

### Chain().new

[[find in source code]](../../uuosio/chain.py#L11)

```python
def new(config, genesis, protocol_features_dir, snapshot_dir):
```

### Chain().pack_action_args

[[find in source code]](../../uuosio/chain.py#L394)

```python
def pack_action_args(name, action, args):
```

### Chain().pending_block_producer

[[find in source code]](../../uuosio/chain.py#L168)

```python
def pending_block_producer():
```

### Chain().pending_block_signing_key

[[find in source code]](../../uuosio/chain.py#L171)

```python
def pending_block_signing_key():
```

### Chain().pending_block_time

[[find in source code]](../../uuosio/chain.py#L164)

```python
def pending_block_time():
```

### Chain().pending_producer_block_id

[[find in source code]](../../uuosio/chain.py#L174)

```python
def pending_producer_block_id():
```

### Chain().pending_producers

[[find in source code]](../../uuosio/chain.py#L189)

```python
def pending_producers(json=True):
```

### Chain().pop_block

[[find in source code]](../../uuosio/chain.py#L371)

```python
def pop_block():
```

### Chain().proposed_producers

[[find in source code]](../../uuosio/chain.py#L195)

```python
def proposed_producers(json=True):
```

### Chain().push_scheduled_transaction

[[find in source code]](../../uuosio/chain.py#L365)

```python
def push_scheduled_transaction(scheduled_tx_id, deadline, billed_cpu_time_us):
```

### Chain().push_transaction

[[find in source code]](../../uuosio/chain.py#L349)

```python
def push_transaction(packed_trx, deadline, billed_cpu_time_us):
```

### Chain().remove_resource_greylist

[[find in source code]](../../uuosio/chain.py#L252)

```python
def remove_resource_greylist(name):
```

### Chain().sender_avoids_whitelist_blacklist_enforcement

[[find in source code]](../../uuosio/chain.py#L225)

```python
def sender_avoids_whitelist_blacklist_enforcement(sender):
```

### Chain().set_action_blacklist

[[find in source code]](../../uuosio/chain.py#L107)

```python
def set_action_blacklist(blacklist):
```

### Chain().set_actor_blacklist

[[find in source code]](../../uuosio/chain.py#L99)

```python
def set_actor_blacklist(blacklist):
```

### Chain().set_actor_whitelist

[[find in source code]](../../uuosio/chain.py#L95)

```python
def set_actor_whitelist(whitelist):
```

### Chain().set_contract_whitelist

[[find in source code]](../../uuosio/chain.py#L103)

```python
def set_contract_whitelist(whitelist):
```

### Chain().set_greylist_limit

[[find in source code]](../../uuosio/chain.py#L321)

```python
def set_greylist_limit(limit):
```

### Chain().set_key_blacklist

[[find in source code]](../../uuosio/chain.py#L111)

```python
def set_key_blacklist(blacklist):
```

### Chain().set_proposed_producers

[[find in source code]](../../uuosio/chain.py#L288)

```python
def set_proposed_producers(producers):
```

### Chain().set_subjective_cpu_leeway

[[find in source code]](../../uuosio/chain.py#L318)

```python
def set_subjective_cpu_leeway(leeway):
```

### Chain().skip_auth_check

[[find in source code]](../../uuosio/chain.py#L294)

```python
def skip_auth_check():
```

### Chain().skip_db_sessions

[[find in source code]](../../uuosio/chain.py#L297)

```python
def skip_db_sessions():
```

### Chain().skip_trx_checks

[[find in source code]](../../uuosio/chain.py#L300)

```python
def skip_trx_checks():
```

### Chain().start_block

[[find in source code]](../../uuosio/chain.py#L30)

```python
def start_block(_time, confirm_block_count=0, features=None):
```

### Chain().startup

[[find in source code]](../../uuosio/chain.py#L18)

```python
def startup(initdb):
```

### Chain().unpack_action_args

[[find in source code]](../../uuosio/chain.py#L399)

```python
def unpack_action_args(name, action, raw_args):
```

### Chain().validate_db_available_size

[[find in source code]](../../uuosio/chain.py#L273)

```python
def validate_db_available_size():
```

### Chain().validate_expiration

[[find in source code]](../../uuosio/chain.py#L267)

```python
def validate_expiration(trx):
```

### Chain().validate_reversible_available_size

[[find in source code]](../../uuosio/chain.py#L276)

```python
def validate_reversible_available_size():
```

### Chain().validate_tapos

[[find in source code]](../../uuosio/chain.py#L270)

```python
def validate_tapos(trx):
```
