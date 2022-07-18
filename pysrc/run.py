import os
import sys
import shlex
import platform
import subprocess
import sysconfig
import argparse

def run_ipyeos(custom_cmds=None):
    if 'RUN_IPYEOS' in os.environ:
        print('run-ipyeos can only be called by python')
        return

    if platform.system() == 'Windows':
        cmd = f'docker run --rm -it -w /root/dev -v "{os.getcwd()}:/root/dev" -t gscdk/test'
        cmd = shlex.split(cmd)
        cmd.append(sys.argv[1:])
        print(' '.join(cmd))
        return subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)

    dir_name = os.path.dirname(os.path.realpath(__file__))
    dir_name = os.path.join(dir_name, "release")
    uuos_program = os.path.join(dir_name, "bin/ipyeos")

    libdir, py_version_short, abiflags = sysconfig.get_config_vars('LIBDIR', 'py_version_short', 'abiflags')

    _system = platform.system()
    if _system == 'Darwin':
        lib_suffix = 'dylib'
        pylib = f'libpython{py_version_short}{abiflags}.dylib'
        os.environ['PYTHON_SHARED_LIB_PATH']=f'{libdir}/{pylib}'
    elif _system == 'Linux':
        lib_suffix = 'so'
        pylib = f'libpython{py_version_short}{abiflags}.so'
        if not 'PYTHON_SHARED_LIB_PATH' in os.environ:
            os.environ['PYTHON_SHARED_LIB_PATH']=f'/usr/lib/x86_64-linux-gnu/{pylib}'
    else:
        raise Exception('Unsupported platform: ' + _system)

    os.environ['CHAIN_API_LIB'] = os.path.join(dir_name, 'lib/libchain_api.' + lib_suffix)
    os.environ['VM_API_LIB'] = os.path.join(dir_name, 'lib/libvm_api.' + lib_suffix)
    os.environ['RUN_IPYEOS']=uuos_program

    cmds = [uuos_program]
    if not custom_cmds:
        cmds.extend(sys.argv[1:])
    else:
        cmds.extend(custom_cmds)
    return subprocess.call(cmds, stdout=sys.stdout, stderr=sys.stderr)

def run_eosnode(custom_cmds=None):
    run_ipyeos(custom_cmds)

def start_debug_server():
    if platform.system() == 'Windows':
        cmd = f'docker run --rm -it -w /root/dev -v "{os.getcwd()}:/root/dev" -t gscdk/test'
        cmd = shlex.split(cmd)
        cmd.append(sys.argv[1:])
        print(' '.join(cmd))
        return subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)

    custom_cmds = ['-m', 'ipyeos', 'eos-debugger']
    custom_cmds.extend(sys.argv[1:])
    run_ipyeos(custom_cmds)
