rm -r pysrc/release
mkdir -p pysrc/release/bin
mkdir -p pysrc/release/lib

cp eos/build/programs/uuos/uuos pysrc/release/bin/uuos || exit 1
cp eos/build/libraries/chain_api/libchain_api.so pysrc/release/lib/libchain_api.so || exit 1
cp eos/build/libraries/vm_api/libvm_api.so pysrc/release/lib/libvm_api.so || exit 1
