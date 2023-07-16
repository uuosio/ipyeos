#pragma once

#include <eosio/eosio.hpp>
#include <eosio/asset.hpp>
#include <eosiolib/capi/eosio/action.h>

using namespace eosio;
using namespace std;

class [[eosio::contract("test")]] test_contract : public eosio::contract {
public:
    using contract::contract;

    struct [[eosio::table("mytable")]] record {
        name    account;
        uint64_t   count;
        uint64_t primary_key() const { return account.value; }
    };

    using record_table = multi_index<"mytable"_n, record>;

    [[eosio::action("inc")]]
    void inc(name n);

    [[eosio::action("getcount")]]
    void getcount(name n);

    [[eosio::action("teststore")]]
    void test_store();

    [[eosio::action("testbound")]]
    void test_bound();

    [[eosio::action("testremove")]]
    void test_remove(name n);
};
