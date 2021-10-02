python3 setup.py sdist bdist_wheel
if [ $? -eq 0 ]; then
./install.sh
fi

