import os
import sys
import platform
import subprocess

class CustomImporter(object):
    def find_module(self, fullname, mpath=None):
#        print('+++find_module', fullname)
        if fullname in ['_chain', '_chainapi']:
            return self
        return

    def load_module(self, module_name):
#        print('+++load_module', module_name)
        from . import _uuos        
        mod = sys.modules.get(module_name)
        if mod is None:
            uuos_module = sys.modules.get('ipyeos._uuos')
            if not uuos_module:
                return
            uuos_so = uuos_module.__file__
            from importlib import util
            spec = util.spec_from_file_location(module_name, uuos_so)
            mod = util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            sys.modules[module_name] = mod
        return mod

sys.meta_path.append(CustomImporter())

def run_pyeos():
    dir_name = os.path.dirname(os.path.realpath(__file__))
    dir_name = os.path.join(dir_name, "release")
    uuos_program = os.path.join(dir_name, "bin/uuos")

    _system = platform.system()
    if _system == 'Darwin':
        lib_suffix = 'dylib'
    elif _system == 'Linux':
        lib_suffix = 'so'
    else:
        raise Exception('Unsupported platform: ' + _system)

    os.environ['CHAIN_API_LIB'] = os.path.join(dir_name, 'lib/libchain_api.' + lib_suffix)
    os.environ['VM_API_LIB'] = os.path.join(dir_name, 'lib/libvm_api.' + lib_suffix)
    os.environ['PYTHON_SHARED_LIB_PATH']='/usr/lib/x86_64-linux-gnu/libpython3.7m.so'
    os.environ['RUN_UUOS']=uuos_program

    cmd = sys.argv[:]
    cmd[0] = uuos_program
    return subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)

if 'RUN_UUOS' in os.environ:
    from . import _uuos
    import _chainapi
    import _chain
