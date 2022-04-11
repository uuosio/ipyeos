./release.sh || exit 1
python3.9 setup.py sdist bdist_wheel --plat-name macosx-10.16-x86_64
if [ $? -eq 0 ]; then
./install.sh
fi

