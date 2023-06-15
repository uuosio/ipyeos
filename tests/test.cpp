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
