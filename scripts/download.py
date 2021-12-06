import os
import subprocess

files = [
    'ipyeos-0.1.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl',
    'ipyeos-0.1.2-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl',
    'ipyeos-0.1.2-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl',
    'ipyeos-0.1.2-cp37-cp37m-manylinux_2_17_x86_64.manylinux2014_x86_64.whl'
]

url = 'https://github.com/uuosio/pyeos/releases/download/v0.1.2/'
for f in files:
    if not os.path.exists(f):
        subprocess.call(['wget', url + f])
