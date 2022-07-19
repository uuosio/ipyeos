import os
import sys
import argparse
from ipyeos import run

INIT_SUCCESS = 6

def main():
    if 'RUN_IPYEOS' in os.environ:
        from ipyeos import eos
        from ipyeos import server
        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers(dest='subparser')

        debug_sub_parser = subparser.add_parser('eos-debugger', help='start eos debugger server')
        debug_sub_parser.add_argument('--addr', default="127.0.0.1", help="eos debugger server address")
        debug_sub_parser.add_argument('--server-port', default="9090", help="eos debugger server port")
        debug_sub_parser.add_argument('--vm-api-port', default="9092", help="eos debugger vm api port")
        debug_sub_parser.add_argument('--apply-request-addr', default="127.0.0.1", help="client side apply request server address")
        debug_sub_parser.add_argument('--apply-request-port', default="9091", help="client side apply request server port")

        start_eos_parser = subparser.add_parser('eos-node', help='run a eos node')

        if sys.argv[1] == 'eos-node':
            argv = sys.argv[1:]
            argv[0] = 'ipyeos'
            ret = eos.init(argv)
            if not ret == INIT_SUCCESS: #exit on not init success
                sys.exit(ret)
            eos.exec()
            print('done!')
        else:
            result, unknown = parser.parse_known_args()
            if result.subparser == 'eos-debugger':
                server.start_debug_server(result.addr, result.server_port, result.vm_api_port, result.apply_request_addr, result.apply_request_port)
            else:
                parser.print_help()
    else:
        custom_cmds = ['-m', 'ipyeos']
        custom_cmds.extend(sys.argv[1:])
        run.run_ipyeos(custom_cmds)

if __name__ == "__main__":
    main()
