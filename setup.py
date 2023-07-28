import os
import sys
import platform

from setuptools import find_packages, setup, Extension
from Cython.Build import cythonize

os.environ["CC"] = "clang"
os.environ["CXX"] = "clang++"

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

dir_name = os.path.dirname(os.path.realpath(__file__))

if platform.system() == 'Darwin':
    extra_link_args=[f'-Wl,-exported_symbols_list,{dir_name}/src/symbols.list']
else:
    extra_link_args=[f'-Wl,--version-script,{dir_name}/src/version.script']

ext_modules = [
    Extension(
        'ipyeos._eos',
        sources=[
            'src/_ipyeos.cpp',
            'src/_vm_api_.cpp',
            'src/_block_log.pyx',
            'src/_chain.pyx',
            'src/_chainapi.pyx',
            'src/_database.pyx',
            'src/_eos.pyx',
            'src/_vm_api.pyx',
            'src/_transaction.pyx',
            'src/_trace_api.pyx',
            'src/_snapshot.pyx',
            'src/_state_history.pyx'
        ],
        include_dirs=[
            'src',
            'leap/libraries/chain_api',
            'leap/libraries/chain/chain_api',
            'leap/libraries/chain/vm_api'
        ],
        language='c++',
        extra_compile_args=['-std=c++17'],
        extra_link_args=extra_link_args,
    )
]

packages=[
    'ipyeos',
    'ipyeos.interfaces',
    'ipyeos.tests',
    'ipyeos.tests.contracts',
    'ipyeos.tests.contracts.micropython',
]

if os.path.exists('pysrc/release'):
    packages.extend([
        'ipyeos.release.bin',
        'ipyeos.release.lib',
    ])

setup(
    name="ipyeos",
    version="0.4.7",
    description="IPYEOS project",
    author='The IPYEOS Team',
    license="MIT",
    packages=packages,
    package_dir={
        'ipyeos': 'pysrc',
        'ipyeos.interfaces': 'pysrc/interfaces',
        'ipyeos.tests': 'pysrc/tests',
        'ipyeos.tests.contracts': 'pysrc/tests/contracts',
        'ipyeos.release.bin': 'pysrc/release/bin',
        'ipyeos.release.lib': 'pysrc/release/lib',
        'ipyeos.tests.contracts.micropython': 'pysrc/tests/contracts/micropython',
    },
    package_data={'ipyeos': release_files},
    ext_modules=cythonize(
        ext_modules,
        compiler_directives={'language_level': 3, },
    ),
    install_requires=[
        'thrift>=0.16.0',
        'pytest>=6.2.5',
        'pyyaml',
        "uvicorn",
        "fastapi",
        "pydantic",
        'aiomonitor',
        'uvloop',
        'aiocache',
        'ipython',
        'ipykernel'
    ],
    tests_require=[],
    include_package_data=True
)