import sys

def load_modules():
    if f'ipyeos._chain' in sys.modules:
        return

    from . import _eos

    modules = ['_chain', '_chainapi', '_vm_api', '_database', '_block_log', '_transaction', '_trace_api']
    ipyeos_module = sys.modules.get('ipyeos._eos')
    assert ipyeos_module, 'ipyeos._eos module not found'
    ipyeos_eos_so = ipyeos_module.__file__

    from importlib import util
    for module_name in modules:
        spec = util.spec_from_file_location(module_name, ipyeos_eos_so)
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sys.modules[f'ipyeos.{module_name}'] = mod
