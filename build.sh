./release.sh || exit 1
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    python3 setup.py sdist bdist_wheel --plat-name manylinux1_x86_64
elif [[ "$OSTYPE" == "darwin"* ]]; then
    python3 setup.py sdist bdist_wheel --plat-name macosx-10.15-x86_64
else
        exit -1
fi
if [ $? -eq 0 ]; then
./install.sh
fi
