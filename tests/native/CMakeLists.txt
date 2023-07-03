cmake_minimum_required( VERSION 3.8 )

project(NATIVE)

add_library( native SHARED
    native.c
)

find_library(VM_API_LIBRARY NAMES vm_api PATHS ${CMAKE_CURRENT_SOURCE_DIR}/../../pysrc/release/lib)

if(NOT VM_API_LIBRARY)
    message(FATAL_ERROR "vm_api Library not found")
endif()

message(STATUS ${VM_API_LIBRARY})

target_link_libraries( native PRIVATE ${VM_API_LIBRARY})
