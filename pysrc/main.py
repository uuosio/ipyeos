import sys
from ipyeos import eos

INIT_SUCCESS = 6

def run():
    ret = eos.init()
    if not ret == INIT_SUCCESS: #exit on not init success
        sys.exit(ret)
    eos.exec()
    print('done!')

if __name__ == "__main__":
    run()
