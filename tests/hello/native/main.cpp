#include <stdint.h>
#include <eosio/eosio.hpp>
#include "hello.hpp"

template<typename T, typename... Args>
bool native_execute_action( name self, name code, void (T::*func)(Args...)  ) {
    size_t size = action_data_size();

    //using malloc/free here potentially is not exception-safe, although WASM doesn't support exceptions
    constexpr size_t max_stack_buffer_size = 512;
    void* buffer = nullptr;
    if( size > 0 ) {
        buffer = max_stack_buffer_size < size ? malloc(size) : alloca(size);
        read_action_data( buffer, size );
    }

    std::tuple<std::decay_t<Args>...> args;
    datastream<const char*> ds((char*)buffer, size);
    ds >> args;

    // if there is an exception throw from action in debug mode, do not call destructor to avoid mess up by exception throw from destructor.
    T *inst = new T(self, code, ds);

    auto f2 = [&]( auto... a ){
        ((inst)->*func)( a... );
    };

    boost::mp11::tuple_apply( f2, args );
    if ( max_stack_buffer_size < size ) {
        free(buffer);
    }
    delete inst;
    return true;
}

extern "C" int native_apply(uint64_t receiver, uint64_t first_receiver, uint64_t action) {
    if (first_receiver == receiver) {
        switch(action) {
            case "hi"_n.value:
            native_execute_action( eosio::name(receiver), eosio::name(first_receiver), &hello::hi );
            break;
            case "check"_n.value:
            native_execute_action( eosio::name(receiver), eosio::name(first_receiver), &hello::check );
            break;
        }
    }
    if (first_receiver != receiver) {
    }
    return 1;
}

