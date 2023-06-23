#pragma once

#include <eosio/eosio.hpp>
#include <eosio/asset.hpp>

using namespace eosio;
using namespace std;

class [[eosio::contract("test")]] test_contract : public eosio::contract {
public:
    using contract::contract;

    struct [[eosio::table("mytable")]] record {
        uint64_t    primary;
        uint64_t    data;
        uint64_t    secondary1;
        uint128_t   secondary2;
        checksum256 secondary3;
        double      secondary4;
        long double secondary5;
        uint64_t primary_key() const { return primary; }
        uint64_t get_secondary1() const { return secondary1; }
        uint128_t get_secondary2() const { return secondary2; }
        checksum256 get_secondary3() const { return secondary3; }
        double get_secondary4() const { return secondary4; }
        long double get_secondary5() const { return secondary5; }
    };

    using record_table = multi_index<"mytable"_n,
                record,
                indexed_by< "bysecondary1"_n,
                const_mem_fun<record, uint64_t, &record::get_secondary1> >,
                indexed_by< "bysecondary2"_n,
                const_mem_fun<record, uint128_t, &record::get_secondary2> >,
                indexed_by< "bysecondary3"_n,
                const_mem_fun<record, checksum256, &record::get_secondary3> >,
                indexed_by< "bysecondary4"_n,
                const_mem_fun<record, double, &record::get_secondary4> >,
                indexed_by< "bysecondary5"_n,
                const_mem_fun<record, long double, &record::get_secondary5> >
                 >;

    [[eosio::action("teststore")]]
    void test_store(uint64_t key,
                uint64_t    secondary1,
                uint128_t   secondary2,
                checksum256 secondary3,
                double      secondary4,
                long double secondary5
    );

    [[eosio::action("testgentx")]]
    void test_generated_tx();

    [[eosio::action("sayhello")]]
    void test_say_hello();

    [[eosio::action("testcmp")]]
    void test_cmp(checksum256 a, checksum256 b);

};
