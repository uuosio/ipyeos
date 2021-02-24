#pragma once

#include <chain_proxy.hpp>
#include <chain_rpc_api_proxy.hpp>
#include <uuos_proxy.hpp>

typedef void (*fn_init_uuos)(uuos_proxy *proxy);
typedef uuos_proxy* (*fn_get_uuos_proxy)();

extern "C" uuos_proxy * get_uuos_proxy();

void uuosext_init();
#define chain(ptr) ((chain_proxy*)ptr)
#define chain_api(ptr) (((chain_proxy*)ptr)->api_proxy())
