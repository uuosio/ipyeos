import sys
from uuosio import uuos

def run():
    ret = uuos.init()
    if not ret == 6: #INIT_SUCCESS
        sys.exit(ret)
    uuos.exec()
    print('done!')

if __name__ == "__main__":
    run()
