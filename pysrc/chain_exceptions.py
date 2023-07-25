import dataclasses
import json
from typing import Dict, List, Optional

from .native_modules import _eos

# exception example:
# {
#     'code': 3170014,
#     'name': 'snapshot_request_not_found',
#     'message': 'Snapshot request not found',
#     'stack': [
#         {
#             'context': {
#                 'level': 'error',
#                 'file': 'snapshot_scheduler.cpp',
#                 'line': 82,
#                 'method': 'unschedule_snapshot',
#                 'hostname': '',
#                 'thread_name': 'ipyeos',
#                 'timestamp': '2023-07-11T14:39:45.256'
#             },
#             'format': 'Snapshot request not found',
#             'data': {}
#         }
#     ]
# }
# {
#     "code":13,
#     "name":"N5boost10wrapexceptISt11logic_errorEE",
#     "message":"could not insert object, most likely a uniqueness constraint was violated",
#     "stack":[
#         {
#             "context":{
#                 "level":"warn",
#                 "file":"chain_proxy.cpp",
#                 "line":74,
#                 "method":"startup",
#                 "hostname":"",
#                 "thread_name":"ipyeos",
#                 "timestamp":"2023-07-11T14:50:29.703"
#               },
#               "format":"rethrow ${what}: ",
#               "data":{
#                     "what":"could not insert object, most likely a uniqueness constraint was violated"
#               }
#         }
#     ]
# }

# {'id': 'de07fe43fc85f6e96a12196abceb994a75ce735ab910b07e5ccb6e6534774f5d',
#  'block_num': 2,
#  'block_time': '2023-07-14T03:20:09.500',
#  'elapsed': 208,
#  'net_usage': 0,
#  'scheduled': False,
#  'action_traces': [],
#  'failed_dtrx_trace': None,
#  'except': {'code': 3040005,
#   'name': 'expired_tx_exception',
#   'message': 'Expired Transaction',
#   'stack': [{'context': {'level': 'error',
#      'file': 'controller.cpp',
#      'line': 3479,
#      'method': 'validate_expiration',
#      'hostname': '',
#      'thread_name': 'ipyeos',
#      'timestamp': '2023-07-14T03:20:09.871'},
#     'format': 'transaction has expired, expiration is ${trx.expiration} and pending block time is ${pending_block_time}',
#     'data': {'trx.expiration': '2018-06-01T12:01:00',
#      'pending_block_time': '2023-07-14T03:20:09.500'}},
#    {'context': {'level': 'warn',
#      'file': 'controller.cpp',
#      'line': 3486,
#      'method': 'validate_expiration',
#      'hostname': '',
#      'thread_name': 'ipyeos',
#      'timestamp': '2023-07-14T03:20:09.871'},
#     'format': '',
#     'data': {'trx': {'expiration': '2018-06-01T12:01:00',
#       'ref_block_num': 1,
#       'ref_block_prefix': 631322306,
#       'max_net_usage_words': 0,
#       'max_cpu_usage_ms': 0,
#       'delay_sec': 0,
#       'context_free_actions': [],
#       'actions': [{'account': 'eosio',
#         'name': 'newaccount',
#         'authorization': [{'actor': 'eosio', 'permission': 'active'}],
#         'data': '0000000000ea3055008037f500ea305501000000010002c0ded2bc1f1305fb0faac5e6c03ee3a1924234985427b6167ca569d13df435cf0100000001000000010002c0ded2bc1f1305fb0faac5e6c03ee3a1924234985427b6167ca569d13df435cf01000000'}],
#       'transaction_extensions': []}}}]},
#  'error_code': '10000000000000000000'}

@dataclasses.dataclass
class Context:
    level: str
    file: str
    line: int
    method: str
    hostname: str
    thread_name: str
    timestamp: str

    def __repr__(self):
        return json.dumps(dataclasses.asdict(self))

    def __str__(self):
        return repr(self)

@dataclasses.dataclass
class Stack:
    context: Context
    format: str
    data: Dict
    message: str

    def __repr__(self):
        return json.dumps(dataclasses.asdict(self))

    def __str__(self):
        return repr(self)

@dataclasses.dataclass
class ChainException(Exception):
    code: int
    name: str
    message: str
    stack: List[Stack]

    def __repr__(self):
        return json.dumps(dataclasses.asdict(self))

    def __str__(self):
        return repr(self)
    
    def asdict(self):
        return dataclasses.asdict(self)

# {'id': 'de07fe43fc85f6e96a12196abceb994a75ce735ab910b07e5ccb6e6534774f5d',
#  'block_num': 2,
#  'block_time': '2023-07-14T03:20:09.500',
#  'elapsed': 208,
#  'net_usage': 0,
#  'scheduled': False,
#  'action_traces': [],
#  'failed_dtrx_trace': None,

@dataclasses.dataclass
class TransactionException(ChainException):
    id: str
    block_num: int
    block_time: str
    elapsed: int
    net_usage: int
    scheduled: bool
    action_traces: List
    failed_dtrx_trace: Optional
    except_: ChainException

    def __repr__(self):
        return json.dumps(dataclasses.asdict(self))

    def __str__(self):
        return repr(self)

# snapshot_request_not_found
class SnapshotRequestNotFoundException(ChainException):
    pass

# unlinkable_block_exception
class UnlinkableBlockException(ChainException):
    pass

# fork_database_exception
class ForkDatabaseException(ChainException):
    pass

# database_guard_exception
class DatabaseGuardException(ChainException):
    pass

# invalid_snapshot_request
class InvalidSnapshotRequestException(ChainException):
    pass

# assert_exception
class AssertException(ChainException):
    pass

# expired_tx_exception
class ExpiredTransactionException(ChainException):
    pass

# block_validate_exception
class BlockValidateException(ChainException):
    pass

# set_exact_code
class SetExactCodeException(ChainException):
    pass

exceptions = {
    'unlinkable_block_exception': UnlinkableBlockException,
    'fork_database_exception': ForkDatabaseException,
    'snapshot_request_not_found': SnapshotRequestNotFoundException,
    'database_guard_exception': DatabaseGuardException,
    'invalid_snapshot_request': InvalidSnapshotRequestException,
    'assert_exception': AssertException,
    'expired_tx_exception': ExpiredTransactionException,
    'block_validate_exception': BlockValidateException,
    'set_exact_code': SetExactCodeException,
}

def new_chain_exception(error: Dict):
    name = error['name']

    stacks = []
    for s in error['stack']:
        message = s['format'].replace('${', '{').format(**s['data'])
        stack = Stack(context=Context(**s['context']), format=s['format'], data=s['data'], message=message)
        stacks.append(stack)

    args = error['code'], error['name'], error['message'], stacks

    try:
        return exceptions[name](*args)
    except KeyError:
        return ChainException(*args)

def get_last_exception(error: Optional[str] = None):
    if error is None:
        error = _eos.get_last_error()
    if not error:
        return None

    try:
        error = json.loads(error)
    except:
        return Exception(error)

    return new_chain_exception(error)

def get_transaction_exception(error: Optional[Dict] = None):
    if not error:
        error = _eos.get_last_error()
        if not error:
            return None
        try:
            error = json.loads(error)
        except:
            return Exception(error)

    if 'except' in error:
        except_ = new_chain_exception(error['except'])
        return TransactionException(except_=except_, **error)
    return new_chain_exception(error)
