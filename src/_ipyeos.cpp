#include <dlfcn.h>
#include <stacktrace.h>

#include "_ipyeos.hpp"

using namespace std;

static fn_get_ipyeos_proxy s_get_ipyeos_proxy = nullptr;

void eosext_init() {
    const char * chain_api_lib = getenv("CHAIN_API_LIB");
    // printf("\n++++chain_api_lib %s\n", chain_api_lib);
    if (chain_api_lib == nullptr) {
        printf("+++CHAIN_API_LIB environment variable not set!");
        exit(-1);
        return;
    }
    void *handle = dlopen(chain_api_lib, RTLD_LAZY | RTLD_GLOBAL);
//    printf("+++++++++chain_api_lib handle %p\n", handle);
    if (handle == 0) {
        printf("Failed to load %s! error: %s\n", chain_api_lib, dlerror());
        exit(-1);
        return;
    }

    s_get_ipyeos_proxy = (fn_get_ipyeos_proxy)dlsym(handle, "get_ipyeos_proxy");
    if (s_get_ipyeos_proxy == nullptr) {
        printf("++++Failed to load chain_new! error: %s\n", dlerror());
        exit(-1);
        return;
    }

}

ipyeos_proxy* get_ipyeos_proxy() {
    if (s_get_ipyeos_proxy == nullptr) {
        printf("++++get_ipyeos_proxy not initialized\n");
        print_stacktrace();
        exit(-1);
        return nullptr;
    }
    return s_get_ipyeos_proxy();
}

static std::exception_ptr last_exception;

void save_last_exception() {
    last_exception = std::current_exception();
}

void clear_last_exception() {
    last_exception = nullptr;
}

bool has_last_exception() {
    return last_exception != nullptr;
}

std::exception_ptr get_last_exception() {
    return last_exception;
}

extern "C" int native_apply(uint64_t a, uint64_t b, uint64_t c) {
    int ret = python_native_apply(a, b, c);
    auto eptr = get_last_exception();
    if (eptr) {
        clear_last_exception();
        std::rethrow_exception(eptr);
    }
    return ret;
}
