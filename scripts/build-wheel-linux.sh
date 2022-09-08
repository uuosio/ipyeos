./scripts/prepare.sh

ln -sf /opt/python/cp38-cp38/bin/cython /usr/local/bin/cython
python3.8 setup.py sdist bdist_wheel

ln -sf /opt/python/cp39-cp39/bin/cython /usr/local/bin/cython
python3.9 setup.py sdist bdist_wheel

ln -sf /opt/python/cp310-cp310/bin/cython /usr/local/bin/cython
python3.10 setup.py sdist bdist_wheel

IPYEOS_VERSION=0.2.14

pushd dist
python3.8 ../scripts/audit.py repair --plat manylinux_2_17_x86_64 ipyeos-$IPYEOS_VERSION-cp38-cp38-linux_x86_64.whl
python3.9 ../scripts/audit.py repair --plat manylinux_2_17_x86_64 ipyeos-$IPYEOS_VERSION-cp39-cp39-linux_x86_64.whl
python3.10 ../scripts/audit.py repair --plat manylinux_2_17_x86_64 ipyeos-$IPYEOS_VERSION-cp310-cp310-linux_x86_64.whl
popd
