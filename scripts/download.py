import os
import sys
import time
import subprocess

version = sys.argv[1]
files = [
    # f'ipyeos-{version}-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl',
    # f'ipyeos-{version}-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl',
    # f'ipyeos-{version}-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl',
    # f'ipyeos-{version}-cp37-cp37m-manylinux_2_17_x86_64.manylinux2014_x86_64.whl',
    f'ipyeos-{version}-cp39-cp39-macosx_10_16_x86_64.whl',
    f'ipyeos-{version}-cp310-cp310-macosx_10_16_x86_64.whl',
    f'ipyeos-{version}-cp37-cp37m-macosx_10_16_x86_64.whl',
    f'ipyeos-{version}-cp38-cp38-macosx_10_16_x86_64.whl',
]

# url = f'https://github.com/uuosio/pyeos/archive/refs/tags/v{version}.tar.gz'
# subprocess.call(['wget', url])

url = f'https://github.com/uuosio/pyeos/releases/download/v{version}/'
for f in files:
    count = 3*60*60/10
    while True:
        print('Downloading {}'.format(f))
        subprocess.call(['wget', url + f])
        if os.path.exists(f):
            break
        time.sleep(10)
        count -= 1
        if count <= 0:
            break
