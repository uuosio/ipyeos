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

        debug_sub_parser = subparser.add_parser('start-debug-server')
        debug_sub_parser.add_argument('--addr', default="127.0.0.1")
        debug_sub_parser.add_argument('--server-port', default="9090")
        debug_sub_parser.add_argument('--apply-request-port', default="9092")

        start_eos_parser = subparser.add_parser('start-eos')

        result, unknown = parser.parse_known_args()

        if result.subparser == 'start-debug-server':
            server.start_debug_server(result.addr, result.server_port, result.apply_request_port)
        elif result.subparser == 'start-eos':
            print(sys.argv)
            argv = sys.argv[1:]
            argv[0] = 'ipyeos'
            ret = eos.init(argv)
            if not ret == INIT_SUCCESS: #exit on not init success
                sys.exit(ret)
            eos.exec()
            print('done!')
        else:
            argv = sys.argv[1:]
            argv.extend(['-i'])
            ret = eos.init()
            if not ret == INIT_SUCCESS: #exit on not init success
                sys.exit(ret)
            eos.exec()
            print('done!')
    else:
        run.run_ipyeos()

if __name__ == "__main__":
    main()
