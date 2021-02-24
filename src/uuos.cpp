#include <dlfcn.h>
#include <stacktrace.h>

#include "uuos.hpp"

using namespace std;

static fn_get_uuos_proxy s_get_uuos_proxy = nullptr;

void uuosext_init() {
    const char * chain_api_lib = getenv("CHAIN_API_LIB");
    printf("++++chain_api_lib %s\n", chain_api_lib);
    if (chain_api_lib == nullptr) {
        printf("+++CHAIN_API_LIB environment variable not set!");
        exit(-1);
        return;
    }
    void *handle = dlopen(chain_api_lib, RTLD_LAZY | RTLD_GLOBAL);
    printf("+++++++++chain_api_lib handle %p\n", handle);
    if (handle == 0) {
        printf("loading %s failed! error: %s\n", chain_api_lib, dlerror());
        exit(-1);
        return;
    }

    s_get_uuos_proxy = (fn_get_uuos_proxy)dlsym(handle, "get_uuos_proxy");
    if (s_get_uuos_proxy == nullptr) {
        printf("++++loading chain_new failed! error: %s\n", dlerror());
        exit(-1);
        return;
    }

}

uuos_proxy* get_uuos_proxy() {
    if (s_get_uuos_proxy == nullptr) {
        printf("++++get_uuos_proxy not initialized\n");
        print_stacktrace();
        exit(-1);
        return nullptr;
    }
    return s_get_uuos_proxy();
}
