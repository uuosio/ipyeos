import argparse
import sys


def parse_args(cmds=None):
    if not cmds:
        cmds = sys.argv[1:]

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
    start_eos_parser.add_argument('-c', '--config-file', default="config.yaml", help="config file for eosnode, default to config.yaml")
    start_eos_parser.add_argument('-s', '--snapshot-file', default="", help="snapshot file for eosnode")
    start_eos_parser.add_argument('-g', '--genesis-file', default="", help="genesis file for eosnode")

    pyeos_parser = subparser.add_parser('pyeosnode', help='run a eos node in python')
    pyeos_parser.add_argument('-c', '--config-file', default="config.yaml", help="config file for pyeosnode, default to config.yaml")
    pyeos_parser.add_argument('-s', '--snapshot-file', default="", help="snapshot file for quick restore network state, default to empty string")
    pyeos_parser.add_argument('-g', '--genesis-file', default="", help="genesis file, default to empty string")

    result = parser.parse_args(cmds)
    return result

def parse_parent_process_args(cmds=None):
    if not cmds:
        cmds = sys.argv[1:]
    parser = argparse.ArgumentParser(cmds)
    parser.add_argument('--addr', default="127.0.0.1", help="eos debugger server address, default to 127.0.0.1")
    parser.add_argument('--server-port', default="9090", help="eos debugger server port, default to 9090")
    parser.add_argument('--vm-api-port', default="9092", help="eos debugger vm api port, default to 9092")
    parser.add_argument('--rpc-server-port', default="9093", help="rpc server port, default to 9093")
    parser.add_argument('--apply-request-addr', default="127.0.0.1", help="client side apply request server address, default to 127.0.0.1")
    parser.add_argument('--apply-request-port', default="9091", help="client side apply request server port, default to 9091")

    result = parser.parse_args(cmds)
    return result
