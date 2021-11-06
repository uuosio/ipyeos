import os
import sys
import platform
from setuptools import find_packages
from skbuild import setup

# Require pytest-runner only when running tests
pytest_runner = (['pytest-runner>=2.0,<3dev']
                 if any(arg in sys.argv for arg in ('pytest', 'test'))
                 else [])

setup_requires = pytest_runner


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
    name="uuosio",
    version="0.1.0",
    description="UUOSIO project",
    author='The UUOSIO Team',
    license="MIT",
    packages=['uuosio'],
    package_dir={'uuosio': 'pysrc'},
    package_data={'uuosio': release_files},

    scripts=['bin/run-uuos'],
    install_requires=['mpy-cross', 'ujson'],
    tests_require=['pytest'],
    setup_requires=setup_requires,
    include_package_data=True
)
