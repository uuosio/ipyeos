#pragma once

#include <chain_proxy.hpp>
#include <chain_rpc_api_proxy.hpp>
#include <ipyeos_proxy.hpp>
#include <vm_api_proxy.hpp>

typedef void (*fn_init_uuos)(ipyeos_proxy *proxy);
typedef ipyeos_proxy* (*fn_get_ipyeos_proxy)();

extern "C" ipyeos_proxy * get_ipyeos_proxy();

void eosext_init();
#define chain(ptr) ((chain_proxy*)ptr)
#define chain_api(ptr) (((chain_proxy*)ptr)->api_proxy())

#define get_vm_api_proxy get_ipyeos_proxy()->get_vm_api_proxy

extern "C" int native_apply(uint64_t a, uint64_t b, uint64_t c);
int python_native_apply(uint64_t a, uint64_t b, uint64_t c);

void save_last_exception();
void clear_last_exception();
bool has_last_exception();
std::exception_ptr get_last_exception();


static inline transaction_proxy *get_transaction_proxy() {
    static transaction_proxy *proxy = nullptr;
    if (proxy == nullptr) {
        proxy = get_ipyeos_proxy()->get_transaction_proxy();
    }
    return proxy;
}

