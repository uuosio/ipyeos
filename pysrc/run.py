import argparse
import asyncio
import os
import platform
import shlex
import signal
import subprocess
import sys
import sysconfig

import aiohttp

from . import args, log
from .debug import get_free_port

logger = log.get_logger(__name__)

dir_name = os.path.dirname(os.path.realpath(__file__))
dir_name = os.path.join(dir_name, "release")
ipyeos_program = os.path.join(dir_name, "bin/ipyeos")

def is_macos_arm():
    return platform.system() == 'Darwin' and platform.processor() == 'arm'

def setup_env():
    port = get_free_port()
    logger.info('++++++++set DEBUG_PORT env to %s', port)
    os.environ['DEBUG_PORT'] = str(port)

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
    os.environ['RUN_IPYEOS']=ipyeos_program
    print('export RUN_IPYEOS=', ipyeos_program, sep='')
    print('export CHAIN_API_LIB=', os.environ['CHAIN_API_LIB'], sep='')
    print('export VM_API_LIB=', os.environ['VM_API_LIB'], sep='')
    print('export PYTHON_SHARED_LIB_PATH=', os.environ['PYTHON_SHARED_LIB_PATH'], sep='')

def run_ipyeos_in_docker():
    cmd = f'docker run --entrypoint ipyeos -it --rm -v "{os.getcwd()}:/develop" -w /develop -t ghcr.io/uuosio/ipyeos'
    cmd = shlex.split(cmd)
    if not custom_cmds:
        cmd.extend(sys.argv[1:])
    else:
        cmd.extend(custom_cmds)
    print(' '.join(cmd))
    return subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)

def quit_app():
    try:
        async def main():
            if sys.argv[0].endswith('__main__.py'): # python3 -m ipyeos ...
                command = sys.argv[3]
            else:
                command = sys.argv[0]
            if command.endswith('eosdebugger'):
                command = 'eosdebugger'
            elif command.endswith('eosnode'):
                command = 'eosnode'
            elif command.endswith('pyeosnode'):
                command = 'pyeosnode'
            elif command.endswith('ipyeos'):
                cmds = sys.argv[3:]
                result = args.parse_args(cmds)
                command = result.subparser
            else:
                logger.info('unknow command: %s', sys.argv)
                return

            if command == 'eosdebugger':
                result = args.parse_parent_process_args()
                url = f'http://{result.addr}:{result.rpc_server_port}/api/quit'
            elif command in ['eosnode', 'pyeosnode']:
                url = f'http://127.0.0.1:{os.environ["DEBUG_PORT"]}/quit'
            else:
                logger.info('unknow command: %s', sys.argv)

            # url = 'http://127.0.0.1:9093/api/quit'
            # r = httpx.post(url, json={}, proxies=None)
            # print(r.status_code, r.text)
            # return
            print('+++++++url:', url)
            async with aiohttp.ClientSession(trust_env=False) as session:
                try:
                    async with session.post(url, data="{}", proxy=None) as resp:
                        print(resp.status)
                        print(await resp.text())
                except Exception as e:
                    print(e)
            print('send quit command to ipyeos done!')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except Exception as e:
        print(e)

def run_ipyeos(custom_cmds=None):
    if 'RUN_IPYEOS' in os.environ:
        print('ipyeos command can only be called by python')
        return

    if platform.system() == 'Windows' or is_macos_arm():
        return run_ipyeos_in_docker()

    setup_env()
    cmds = [ipyeos_program]
    if not custom_cmds:
        cmds.extend(sys.argv[1:])
    else:
        cmds.extend(custom_cmds)
    print(' '.join(cmds))
    try:
        p = subprocess.Popen(cmds, stdout=sys.stdout, stderr=sys.stderr)
        ret = p.wait()
        logger.info('ipyeos exit with code: %s', ret)
        return ret
    except KeyboardInterrupt:
        # quit_app()
        # p.terminate()
        # p.send_signal(signal.SIGINT)
        logger.info('KeyboardInterrupt, wait for ipyeos exit...')
        ret = p.wait()
        logger.info('ipyeos exit with code: %s', ret)
        return ret

def start_debug_server():
    if platform.system() == 'Windows':
        cmd = f'docker run --rm -it -w /root/dev -v "{os.getcwd()}:/root/dev" -p 9090:9090 -p 9092:9092 -p 9093:9093 -t ghcr.io/uuosio/ipyeos'
        cmd = shlex.split(cmd)
        cmd.extend(sys.argv[1:])
        print(' '.join(cmd))
        return subprocess.call(cmd, stdout=sys.stdout, stderr=sys.stderr)

    custom_cmds = ['-m', 'ipyeos', 'eosdebugger']
    custom_cmds.extend(sys.argv[1:])
    run_ipyeos(custom_cmds)

def run_program(program):
    dir_name = os.path.dirname(os.path.realpath(__file__))
    dir_name = os.path.join(dir_name, "release")
    program = os.path.join(dir_name, f"bin/{program}")

    cmds = [program]
    cmds.extend(sys.argv[1:])
    print(' '.join(cmds))
    try:
        p = subprocess.Popen(cmds, stdout=sys.stdout, stderr=sys.stderr)
        ret = p.wait()
        return ret
    except KeyboardInterrupt:
        p.terminate()
        ret = p.wait()
        return ret
