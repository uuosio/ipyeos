import sys
from ipyeos import uuos

INIT_SUCCESS = 6

def run():
    ret = uuos.init()
    if not ret == INIT_SUCCESS: #exit on not init success
        sys.exit(ret)
    uuos.exec()
    print('done!')

if __name__ == "__main__":
    run()
