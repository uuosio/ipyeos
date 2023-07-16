#include "test.hpp"

[[eosio::action("inc")]]
void test_contract::inc(name n) {
    print_f("++++++++++name %\n", n);
    // return;
    // require_auth(n);

    record_table mytable(get_self(), 0);
    
    auto itr = mytable.find(n.value);

    name payer = get_self();

    if (mytable.end() == itr) {
        mytable.emplace( payer, [&]( auto& row ) {
            row.account = n;
            row.count = 1;
            print_f("++++++++++emplace: count %", row.count);
            set_action_return_value((void *)&row.count, sizeof(row.count));
        });
    } else {
        mytable.modify( itr, payer, [&]( auto& row ) {
            row.count +=1;
            print_f("++++++++++modify: count %", row.count);
            set_action_return_value((void *)&row.count, sizeof(row.count));
        });
    }
}

[[eosio::action("getcount")]]
void test_contract::getcount(name n) {
    print_f("++++++++++name %\n", n);
    record_table mytable(get_self(), 0);    
    auto itr = mytable.find(n.value);
    if (mytable.end() != itr) {
        print_f("++++++++++get count %\n", itr->count);
    }else {
        print_f("++++++++++get count %\n", 0);
    }
    set_action_return_value((void *)&itr->count, sizeof(itr->count));
}

[[eosio::action("teststore")]]
void test_contract::test_store() {
    record_table mytable(get_self(), 0);
    mytable.emplace( _self, [&]( auto& row ) {
        row.account = name{1};
        row.count = 1;
    });

    mytable.emplace( _self, [&]( auto& row ) {
        row.account = name{3};
        row.count = 1;
    });

    mytable.emplace( _self, [&]( auto& row ) {
        row.account = name{5};
        row.count = 1;
    });
}

[[eosio::action("testbound")]]
void test_contract::test_bound() {
    record_table mytable(get_self(), 0);

    auto it = mytable.lower_bound(1);
    print_f("++++++account: %\n", it->account);

    it = mytable.upper_bound(3);
    print_f("++++++account: %\n", it->account);
}

[[eosio::action("testremove")]]
void test_contract::test_remove(name n) {
    record_table mytable(get_self(), 0);

    auto it = mytable.find(n.value);
    if (mytable.end() != it) {
        mytable.erase(it);
    }
}
