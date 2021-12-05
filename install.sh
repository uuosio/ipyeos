pushd dist
python3.9 -m pip uninstall ipyeos -y;python3.9 -m pip install ./ipyeos-*.whl
popd
