pushd dist
python3 -m pip uninstall ipyeos -y;python3 -m pip install ./ipyeos-*.whl
popd
