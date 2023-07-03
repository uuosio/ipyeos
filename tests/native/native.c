#include <stdint.h>

extern void prints(const char* cstr);

void native_init(void* v) {
}

int native_apply(uint64_t receiver, uint64_t first_receiver, uint64_t action) {
    for (int i=0; i<10; i++) {
        prints("Hello, World!\n");
    }
    return 1;
}
