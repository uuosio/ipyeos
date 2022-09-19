if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    EXT=so
elif [[ "$OSTYPE" == "darwin"* ]]; then
    EXT=dylib
else
        exit -1
fi

BUILD_DIR=build-mac

rm -r pysrc/release
mkdir -p pysrc/release/bin
mkdir -p pysrc/release/lib

cp leap/$BUILD_DIR/programs/ipyeos/ipyeos pysrc/release/bin/ipyeos || exit 1
cp leap/$BUILD_DIR/libraries/chain_api/libchain_api.$EXT pysrc/release/lib/libchain_api.$EXT || exit 1
cp leap/$BUILD_DIR/libraries/vm_api/libvm_api.$EXT pysrc/release/lib/libvm_api.$EXT || exit 1
