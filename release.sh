if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    EXT=so
elif [[ "$OSTYPE" == "darwin"* ]]; then
    EXT=dylib
else
        exit -1
fi

rm -r pysrc/release
mkdir -p pysrc/release/bin
mkdir -p pysrc/release/lib

cp eos/build/programs/ipyeos/ipyeos pysrc/release/bin/ipyeos || exit 1
cp eos/build/libraries/chain_api/libchain_api.$EXT pysrc/release/lib/libchain_api.$EXT || exit 1
cp eos/build/libraries/vm_api/libvm_api.$EXT pysrc/release/lib/libvm_api.$EXT || exit 1
