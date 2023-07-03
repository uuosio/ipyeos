cmake_minimum_required( VERSION 3.8 )

project(NATIVE)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")

add_library( hello_native SHARED
    ../src/hello.cpp
    main.cpp
)

target_compile_options(hello_native PRIVATE
    ${COVERAGE_OPTIONS}
    -DEOSIO_NATIVE
    -Wno-unknown-attributes
    -Wno-deprecated-declarations
    -Wno-unused-value
)

find_library(VM_API_LIBRARY NAMES vm_api PATHS ${CMAKE_CURRENT_SOURCE_DIR}/../../../pysrc/release/lib)

if(NOT VM_API_LIBRARY)
    message(FATAL_ERROR "vm_api Library not found")
endif()

message(STATUS ${VM_API_LIBRARY})

target_link_libraries( hello_native PRIVATE ${VM_API_LIBRARY})

target_include_directories( hello_native PUBLIC 
   ${CMAKE_CURRENT_SOURCE_DIR}/../include
   ${CDT_ROOT}/include
   ${CDT_ROOT}/include/eosiolib/capi
   ${CDT_ROOT}/include/eosiolib/native
   ${CDT_ROOT}/include/eosiolib/core
   ${CDT_ROOT}/include/eosiolib/contracts
)
