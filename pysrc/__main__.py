import os
import sys
import argparse
from ipyeos import run

INIT_SUCCESS = 6

def main():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='subparser')

    debug_sub_parser = subparser.add_parser('eos-debugger', help='start eos debugger server')
    debug_sub_parser.add_argument('--addr', default="127.0.0.1", help="eos debugger server address")
    debug_sub_parser.add_argument('--server-port', default="9090", help="eos debugger server port")
    debug_sub_parser.add_argument('--vm-api-port', default="9092", help="eos debugger vm api port")
    debug_sub_parser.add_argument('--apply-request-addr', default="127.0.0.1", help="client side apply request server address")
    debug_sub_parser.add_argument('--apply-request-port', default="9091", help="client side apply request server port")
    debug_sub_parser.add_argument('--rpc-server-addr', default="127.0.0.1", help="rpc server address")
    debug_sub_parser.add_argument('--rpc-server-port', default="9093", help="rpc server port")

    start_eos_parser = subparser.add_parser('eos-node', help='run a eos node')

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(-1)

    if 'RUN_IPYEOS' in os.environ:
        from ipyeos import eos
        from ipyeos import server

        if sys.argv[1] == 'eos-node':
            argv = sys.argv[1:]
            argv[0] = 'ipyeos'
            ret = eos.init(argv)
            if not ret == INIT_SUCCESS: #exit on not init success
                sys.exit(ret)
            eos.exec()
            print('done!')
        elif sys.argv[1] == 'eos-debugger':
            result, unknown = parser.parse_known_args()
            server.start_debug_server(result.addr, result.server_port, result.vm_api_port, result.apply_request_addr, result.apply_request_port, result.rpc_server_addr,result.rpc_server_port)                
        else:
            parser.print_help()
    else:
        if sys.argv[1] in ['eos-node', 'eos-debugger']:
            custom_cmds = ['-m', 'ipyeos']
            custom_cmds.extend(sys.argv[1:])
            run.run_ipyeos(custom_cmds)
        else:
            run.run_ipyeos()

if __name__ == "__main__":
    main()
