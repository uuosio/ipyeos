if [[ $ARCH == "Darwin" ]]; then
	declare NPROC=$( sysctl -n hw.logicalcpu )
	declare DYLIB_EXT="dylib"
else
	declare NPROC=$( nproc )
	declare DYLIB_EXT="so"
fi


function build_project() {
	local ret=0
	if [ -f "$(pwd)/eos/build/CMakeCache.txt" ]; then
        	pushd eos/build
        	make -j$NPROC
		ret=$?
	        popd
	else
                pushd eos
		./scripts/eosio_build.sh
		ret=$?
                popd
	fi
	return $ret
}

build_project
#cp eos/build/programs/uuos/uuos bin/uuos

if [[ $ARCH == "Darwin" ]]; then
	./build-mac.sh
else
	./build-linux.sh
fi
