add_cython_target(_uuos CXX)
add_cython_target(_chain CXX)
add_cython_target(_chainapi CXX)

add_library(_uuos MODULE
    ${_uuos}
    ${_chain}
    ${_chainapi}
    main.cpp
    uuos.cpp
)

python_extension_module(_uuos)

message(STATUS "++++++++++="$ENV{PROJECT_DIR})

set(PROJECT_DIR $ENV{PROJECT_DIR})

if ("${PROJECT_DIR}" STREQUAL "")
    set(PROJECT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../eos)
endif()

# if (APPLE)
#       set(_symbols_list "${CMAKE_CURRENT_SOURCE_DIR}/symbols.list")
#       set(LINK_FLAGS "${LINK_FLAGS} -Wl,-exported_symbols_list,'${_symbols_list}'")
# else()
#       set(_version_script "${CMAKE_CURRENT_SOURCE_DIR}/version.script")
#       set(LINK_FLAGS "${LINK_FLAGS} -Wl,--version-script,\"${_version_script}\"")
# endif (APPLE)

# set_target_properties(_uuos  PROPERTIES LINK_FLAGS "${LINK_FLAGS}")

target_include_directories(_uuos PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
    ${PROJECT_DIR}/libraries/chain/chain_api
    ${PROJECT_DIR}/libraries/chain_api
)

set_property(TARGET _uuos PROPERTY CXX_STANDARD 17)

install(TARGETS _uuos LIBRARY DESTINATION pysrc)
