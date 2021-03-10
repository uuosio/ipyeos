declare ARCH=$( uname )

if [[ $ARCH == "Darwin" ]]; then
	declare NPROC=$( sysctl -n hw.logicalcpu )
	declare DYLIB_EXT="dylib"
	if [ -f "$(pwd)/eos/build/libraries/vm_api/libvm_api.so" ]; then
		mv "$(pwd)/eos/build" "$(pwd)/eos/build-linux"
	fi

	if [ -d "$(pwd)/eos/build-mac" ]; then
		mv "$(pwd)/eos/build-mac" "$(pwd)/eos/build"
	fi

else
	declare NPROC=$( nproc )
	declare DYLIB_EXT="so"

	if [ -f "$(pwd)/eos/build/libraries/vm_api/libvm_api.dylib" ]; then
		mv "$(pwd)/eos/build" "$(pwd)/eos/build-mac"
	fi

	if [ -d "$(pwd)/eos/build-linux" ]; then
		mv "$(pwd)/eos/build-linux" "$(pwd)/eos/build"
	fi
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

if [[ $? != 0 ]]; then
	exit $?
fi

#cp eos/build/programs/uuos/uuos bin/uuos

if [[ $ARCH == "Darwin" ]]; then
	./scripts/build-mac.sh
else
	./scripts/build-linux.sh
fi
