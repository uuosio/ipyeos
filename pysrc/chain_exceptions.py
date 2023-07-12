import json
import dataclasses
from typing import Dict, List, Optional
from . import _eos

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

# if name == 'unlinkable_block_exception':
#     return UnlinkableBlockException(*args)
# elif name == 'fork_database_exception':
#     return ForkDatabaseException(*args)
# elif name == 'snapshot_request_not_found':
#     return SnapshotRequestNotFoundException(*args)

exceptions = {
    'unlinkable_block_exception': UnlinkableBlockException,
    'fork_database_exception': ForkDatabaseException,
    'snapshot_request_not_found': SnapshotRequestNotFoundException,
    'database_guard_exception': DatabaseGuardException,
}

def get_last_exception(error: Optional[str] = None):
    if error is None:
        error = _eos.get_last_error_and_clear()
    if not error:
        return None

    try:
        error = json.loads(error)
    except:
        return Exception(error)
    name = error['name']

    stacks = []
    for s in error['stack']:
        stack = Stack(context=Context(**s['context']), format=s['format'], data=s['data'])
        stacks.append(stack)

    args = error['code'], error['name'], error['message'], stacks

    try:
        return exceptions[name](*args)
    except KeyError:
        return ChainException(*args)
