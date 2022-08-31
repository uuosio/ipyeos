add_cython_target(_eos CXX)
add_cython_target(_chain CXX)
add_cython_target(_chainapi CXX)
add_cython_target(_vm_api CXX)

add_library(_eos MODULE
    ${_eos}
    ${_chain}
    ${_chainapi}
    ${_vm_api}
    main.cpp
    _ipyeos.cpp
    _vm_api.cpp
)

python_extension_module(_eos)

message(STATUS "++++++++++="$ENV{PROJECT_DIR})

set(PROJECT_DIR $ENV{PROJECT_DIR})

if ("${PROJECT_DIR}" STREQUAL "")
    set(PROJECT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../eos)
endif()

if (APPLE)
    #   set(_symbols_list "${CMAKE_CURRENT_SOURCE_DIR}/symbols.list")
    #   set(LINK_FLAGS "${LINK_FLAGS} -Wl,-exported_symbols_list,'${_symbols_list}'")
else()
    set(_version_script "${CMAKE_CURRENT_SOURCE_DIR}/version.script")
    set(LINK_FLAGS "${LINK_FLAGS} -Wl,--version-script,\"${_version_script}\"")
    set_target_properties(_eos  PROPERTIES LINK_FLAGS "${LINK_FLAGS}")
endif (APPLE)

target_include_directories(_eos PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
    ${PROJECT_DIR}/libraries/chain/chain_api
    ${PROJECT_DIR}/libraries/chain_api
    ${PROJECT_DIR}/libraries/chain/vm_api
)

set_property(TARGET _eos PROPERTY CXX_STANDARD 17)

install(TARGETS _eos LIBRARY DESTINATION pysrc)
