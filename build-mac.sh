CC=clang CXX=clang++ python3.7 setup.py sdist bdist_wheel --plat-name macosx-10.9-x86_64
cp ./_skbuild/macosx-10.9-x86_64-3.7/cmake-install/uuosio/_uuos.cpython-37m-darwin.so .
