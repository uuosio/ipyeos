#include <eosio/transaction.hpp>
#include "test.hpp"

[[eosio::action("teststore")]]
void test_contract::test_store(uint64_t key, checksum256 hash) {
    record_table mytable( get_self(), 0);

    std::array<uint128_t, 2> a1 = {0, 1};
    std::array<uint128_t, 2> a2 = {1, 0};
    printhex((char*)a1.data(), 32);
    print("\n");

    printhex((char*)a2.data(), 32);
    print("\n");


    print(a1 < a2, "\n");
    print(std::less<std::array<uint128_t, 2>>()(a1, a2), "\n");

    auto buf = hash.extract_as_byte_array();
    printhex(buf.data(), buf.size());
    print("\n");

    printhex((char*)hash.data(), 32);
    print("\n");

    mytable.emplace( _self, [&]( auto& row ) {
        row.primary = key;
        row.secondary3 = hash;
        row.data = 3;
    });
}


[[eosio::action("testcmp")]]
void test_contract::test_cmp(checksum256 a, checksum256 b) {
    auto buf = a.extract_as_byte_array();
    printhex(buf.data(), buf.size());
    print("\n");

    printhex((char*)a.data(), 32);
    print("\n");

    buf = b.extract_as_byte_array();
    printhex(buf.data(), buf.size());
    print("\n");

    printhex((char*)b.data(), 32);
    print("\n");

    print(a < b, "\n");
}


[[eosio::action("testgentx")]]
void test_contract::test_generated_tx() {
    print("+++++ test_generated_tx\n");
    // auto trx = transaction(eosio::time_point_sec(0));
    auto trx = transaction(time_point_sec(current_time_point()) + 5);
    std::vector<permission_level> permissions = { {"hello"_n, "active"_n} };

    trx.actions.emplace_back(permissions, "hello"_n, "sayhello"_n, string("hello"));
    trx.send( 1, "hello"_n );
}

[[eosio::action("sayhello")]]
void test_contract::test_say_hello() {
    print("+++++ test_say_hello\n");
    print("hello\n");
}
