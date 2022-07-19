./release.sh || exit 1
python setup.py sdist bdist_wheel
if [ $? -eq 0 ]; then
./install.sh
fi

