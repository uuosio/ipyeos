import argparse
import concurrent.futures
import os
import sys

INIT_SUCCESS = 6

def main():
    if 'RUN_IPYEOS' in os.environ:
        from . import main
        main.run()
    else:
        from . import run
        if sys.argv[1] in ['eosnode', 'eosdebugger']:
            custom_cmds = ['-m', 'ipyeos']
            custom_cmds.extend(sys.argv[1:])
            run.run_ipyeos(custom_cmds)
        else:
            run.run_ipyeos()

if __name__ == "__main__":
    main()
