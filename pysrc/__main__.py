import argparse
import concurrent.futures
import os
import sys

INIT_SUCCESS = 6

def main():
    if 'RUN_IPYEOS' in os.environ:
        from . import main
        return main.run()
    else:
        from . import run
        #python3 -m ipyeos eosnode ...
        #python3 -m ipyeos eosdebugger ...
        if sys.argv[1] in ['eosnode', 'eosdebugger']:
            custom_cmds = ['-m', 'ipyeos']
            custom_cmds.extend(sys.argv[1:])
            run.run_ipyeos(custom_cmds)
        else:
            run.run_ipyeos()

if __name__ == "__main__":
    main()
