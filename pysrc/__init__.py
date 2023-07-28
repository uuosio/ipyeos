import argparse
import os
import platform
import shlex
import subprocess
import sys
import sysconfig

from . import run

__version__ = "0.4.7"

cur_dir = os.path.dirname(os.path.realpath(__file__))

def run_ipyeos(custom_cmds=[]):
    return run.run_ipyeos(custom_cmds)

def run_eosnode():
    custom_cmds=['-m', 'ipyeos', 'eosnode']
    custom_cmds.extend(sys.argv[1:])
    return run.run_ipyeos(custom_cmds)

def run_pyeosnode():
    custom_cmds=['-m', 'ipyeos', 'pyeosnode']
    custom_cmds.extend(sys.argv[1:])
    return run.run_ipyeos(custom_cmds)

def run_nodeos():
    custom_cmds=['nodeos']
    custom_cmds.extend(sys.argv[1:])
    return run.run_ipyeos(custom_cmds)

def run_keosd():
    custom_cmds=['keosd']
    custom_cmds.extend(sys.argv[1:])
    return run.run_ipyeos(custom_cmds)

def run_cleos():
    custom_cmds=['cleos']
    custom_cmds.extend(sys.argv[1:])
    return run.run_ipyeos(custom_cmds)

def start_debug_server():
    return run.start_debug_server()

def run_test():
    if len(sys.argv) == 2:
        cmd = f'ipyeos -m pytest -s -x -o log_cli=true -o log_cli_level=INFO {sys.argv[1]}'
    elif len(sys.argv) == 3:
        cmd = f'ipyeos -m pytest -s -x -o log_cli=true -o log_cli_level=INFO {sys.argv[1]} -k {sys.argv[2]}'
    else:
        print('usage: eostest [test script] [test case]')
        return
    print(cmd)
    cmd = shlex.split(cmd)
    return subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)

def ipyeos_get_dir():
    print(cur_dir)

def ipyeos_get_lib_dir():
    print(f'{cur_dir}/release/lib')
