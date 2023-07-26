import sys
from importlib import util

def load_modules():
    if f'ipyeos._chain' in sys.modules:
        return

    from . import _eos

    modules = ['_chain', '_chainapi', '_vm_api', '_database', '_block_log', '_transaction', '_trace_api', '_snapshot', '_state_history']
    ipyeos_module = sys.modules.get('ipyeos._eos')
    assert ipyeos_module, 'ipyeos._eos module not found'
    ipyeos_eos_so = ipyeos_module.__file__

    for module_name in modules:
        spec = util.spec_from_file_location(module_name, ipyeos_eos_so)
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules[f'ipyeos.{module_name}'] = mod

load_modules()

from . import _eos
from . import _chain
from . import _chainapi
from . import _vm_api
from . import _database
from . import _block_log
from . import _transaction
from . import _trace_api
from . import _snapshot
from . import _state_history

