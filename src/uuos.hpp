#pragma once

#include <chain_proxy.hpp>
#include <chain_rpc_api_proxy.hpp>
#include <uuos_proxy.hpp>
#include <vm_api_proxy.hpp>

typedef void (*fn_init_uuos)(uuos_proxy *proxy);
typedef uuos_proxy* (*fn_get_uuos_proxy)();

extern "C" uuos_proxy * get_uuos_proxy();

void uuosext_init();
#define chain(ptr) ((chain_proxy*)ptr)
#define chain_api(ptr) (((chain_proxy*)ptr)->api_proxy())

#define get_vm_api_proxy get_uuos_proxy()->get_vm_api_proxy

extern "C" void native_apply(uint64_t a, uint64_t b, uint64_t c);
