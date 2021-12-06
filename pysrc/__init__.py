import os
import sys
import platform
import subprocess
import sysconfig

class CustomImporter(object):
    def find_module(self, fullname, mpath=None):
#        print('+++find_module', fullname)
        if fullname in ['_chain', '_chainapi']:
            return self
        return

    def load_module(self, module_name):
#        print('+++load_module', module_name)
        from . import _eos        
        mod = sys.modules.get(module_name)
        if mod is None:
            uuos_module = sys.modules.get('ipyeos._eos')
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

def run_ipyeos():
    dir_name = os.path.dirname(os.path.realpath(__file__))
    dir_name = os.path.join(dir_name, "release")
    uuos_program = os.path.join(dir_name, "bin/uuos")

    libdir, py_version_short, abiflags = sysconfig.get_config_vars('LIBDIR', 'py_version_short', 'abiflags')

    _system = platform.system()
    if _system == 'Darwin':
        lib_suffix = 'dylib'
        pylib = f'libpython{py_version_short}{abiflags}.dylib'
        os.environ['PYTHON_SHARED_LIB_PATH']=f'{libdir}/{pylib}'
    elif _system == 'Linux':
        lib_suffix = 'so'
        pylib = f'libpython{py_version_short}{abiflags}.so'
        os.environ['PYTHON_SHARED_LIB_PATH']=f'/usr/lib/x86_64-linux-gnu/{pylib}'
    else:
        raise Exception('Unsupported platform: ' + _system)

    os.environ['CHAIN_API_LIB'] = os.path.join(dir_name, 'lib/libchain_api.' + lib_suffix)
    os.environ['VM_API_LIB'] = os.path.join(dir_name, 'lib/libvm_api.' + lib_suffix)
    os.environ['RUN_IPYEOS']=uuos_program

    cmd = sys.argv[:]
    cmd[0] = uuos_program
    return subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)

if 'RUN_IPYEOS' in os.environ:
    from . import _eos
    import _chainapi
    import _chain
