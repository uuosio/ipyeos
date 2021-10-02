pushd dist
python3 -m pip uninstall uuosio -y;python3 -m pip install ./uuosio-*.whl
popd
