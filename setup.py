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
    'tester/contracts/eosio.bios/*',
    'tester/contracts/eosio.msig/*',
    'tester/contracts/eosio.system/*',
    'tester/contracts/eosio.token/*',
    'tester/contracts/eosio.wrap/*',
    'tester/contracts/micropython/*',
])

dir_name = os.path.dirname(os.path.realpath(__file__))

if platform.system() == 'Darwin':
    extra_link_args=["-arch", "x86_64", f'-Wl,-exported_symbols_list,{dir_name}/src/symbols.list']
else:
    extra_link_args=["-arch", "x86_64", f'-Wl,--version-script,{dir_name}/src/version.script']

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
            'src/_signed_transaction.pyx',
            'src/_packed_transaction.pyx',
            'src/_trace_api.pyx',
            'src/_snapshot.pyx',
            'src/_state_history.pyx',
            'src/_multi_index.pyx',
            'src/_read_write_lock.pyx',
            'src/_block_state.pyx',
            'src/_transaction_trace.pyx',
            'src/_action_trace.pyx',
            'src/_signed_block.pyx',
        ],
        include_dirs=[
            'src',
            'leap/libraries/chain_api',
            'leap/libraries/chain/chain_api',
            'leap/libraries/chain/vm_api'
        ],
        language='c++',
        extra_compile_args=["-arch", "x86_64", '-std=c++17'],
        extra_link_args=extra_link_args,
    )
]

packages=[
    'ipyeos',
    'ipyeos.bases',
    'ipyeos.extensions',
    'ipyeos.node',
    'ipyeos.tester',
    'ipyeos.tester.interfaces',
    'ipyeos.tester.contracts',
]

if os.path.exists('pysrc/release'):
    packages.extend([
        'ipyeos.release.bin',
        'ipyeos.release.lib',
    ])

setup(
    name="ipyeos",
    version="0.4.9",
    description="IPYEOS project",
    author='The IPYEOS Team',
    license="MIT",
    packages=packages,
    package_dir={
        'ipyeos': 'pysrc',
        'ipyeos.core': 'pysrc/core',
        'ipyeos.bases': 'pysrc/bases',
        'ipyeos.extensions': 'pysrc/extensions',
        'ipyeos.node': 'pysrc/node',
        'ipyeos.tester.interfaces': 'pysrc/tester/interfaces',
        'ipyeos.tester': 'pysrc/tester',
        'ipyeos.release.bin': 'pysrc/release/bin',
        'ipyeos.release.lib': 'pysrc/release/lib',
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
        'aiocache'
    ],
    tests_require=[],
    include_package_data=True
)