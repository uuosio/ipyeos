pushd dist
python3.9 -m pip uninstall ipyeos -y;python3 -m pip install ./ipyeos-*.whl
popd
