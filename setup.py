import os
import sys
import platform
from setuptools import find_packages
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
])

setup(
    name="ipyeos",
    version="0.1.2",
    description="IPYEOS project",
    author='The IPYEOS Team',
    license="MIT",
    packages=['ipyeos'],
    package_dir={'ipyeos': 'pysrc'},
    package_data={'ipyeos': release_files},

    install_requires=['mpy-cross', 'ujson'],
    tests_require=['pytest'],
    include_package_data=True
)
