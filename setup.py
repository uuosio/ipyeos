import os
import sys
import platform
from setuptools import find_packages
if platform.system() == 'Windows':
    from distutils.core import setup
else:
    from skbuild import setup

release_files = []
for root, dirs, files in os.walk("pysrc/release"):
    for f in files:
        release_files.append(os.path.join(root.replace('pysrc/', ''), f))

version = platform.python_version_tuple()
version = '%s.%s' % (version[0], version[1])

release_files.extend([
    'tests/contracts/eosio.bios/*',
    'tests/contracts/eosio.msig/*',
    'tests/contracts/eosio.system/*',
    'tests/contracts/eosio.token/*',
    'tests/contracts/eosio.wrap/*',
    'tests/contracts/micropython/*',
    'tests/test_template.py',
    'tests/activate_kv.wasm',
])

setup(
    name="ipyeos",
    version="0.4.2",
    description="IPYEOS project",
    author='The IPYEOS Team',
    license="MIT",
    packages=[
        'ipyeos',
        'ipyeos.interfaces'
    ],
    package_dir={
        'ipyeos': 'pysrc',
        'ipyeos.interfaces': 'pysrc/interfaces'
    },
    package_data={'ipyeos': release_files},

    install_requires=[
        'thrift>=0.16.0',
        'pytest>=6.2.5',
        'aiohttp>=3.8.4',
        'ipython',
        'ipykernel'
    ],
    tests_require=[],
    include_package_data=True
)