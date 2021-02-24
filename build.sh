if [[ $ARCH == "Linux" ]]; then
	declare NPROC=$( nproc )
	declare DYLIB_EXT="so"
else
	declare NPROC=$( sysctl -n hw.logicalcpu )
	declare DYLIB_EXT="dylib"
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
cp eos/build/programs/uuos/uuos bin/uuos


