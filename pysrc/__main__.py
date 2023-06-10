import argparse
import concurrent.futures
import os
import sys

from . import run

INIT_SUCCESS = 6

def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='subparser')

    debug_sub_parser = subparser.add_parser('eosdebugger', help='start eos debugger server')
    debug_sub_parser.add_argument('--addr', default="127.0.0.1", help="eos debugger server address, default to 127.0.0.1")
    debug_sub_parser.add_argument('--server-port', default="9090", help="eos debugger server port, default to 9090")
    debug_sub_parser.add_argument('--vm-api-port', default="9092", help="eos debugger vm api port, default to 9092")
    debug_sub_parser.add_argument('--rpc-server-port', default="9093", help="rpc server port, default to 9093")
    debug_sub_parser.add_argument('--apply-request-addr', default="127.0.0.1", help="client side apply request server address, default to 127.0.0.1")
    debug_sub_parser.add_argument('--apply-request-port', default="9091", help="client side apply request server port, default to 9091")

    start_eos_parser = subparser.add_parser('eosnode', help='run a eos node')

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(-1)

    if 'RUN_IPYEOS' in os.environ:
        from . import main
        main.run()
    else:
        if sys.argv[1] in ['eosnode', 'eosdebugger']:
            custom_cmds = ['-m', 'ipyeos']
            custom_cmds.extend(sys.argv[1:])
            run.run_ipyeos(custom_cmds)
        else:
            run.run_ipyeos()

if __name__ == "__main__":
    main()
