import chain
def apply(a, b, c):
    r = chain.kv_set('alice', 'hello', 'world', 'alice')
    print(r)
    r = chain.kv_set('alice', 'helloo', 'worldd', 'alice')
    print(r)
    r = chain.kv_set('alice', 'hekkoo', 'worldd', 'alice')
    print(r)
    r = chain.kv_get('alice', 'hello')
    print(r)
    assert r == (True, 5)
    r = chain.kv_get_data(0)
    print('+++kv_get_data:', r)
    assert r == b'world'

    r = chain.kv_get('alice', 'helloo')
    print('kv_get:helloo', r)
    assert r == (True, 6)
    r = chain.kv_get_data(0)
    print('+++kv_get_data:', r)
    assert r == b'worldd'

    itr = chain.kv_it_create('alice', 'hell')
    print(itr)
    ret = chain.kv_it_lower_bound(itr, 'hell')
    print('kv_it_lower_bound:', ret)
    assert ret == (0, 5, 5)

    ret = chain.kv_it_key(itr, 0, 0)
    print('+++kv_it_key:', ret)
    assert ret == (0, 5, b'hello')

    ret = chain.kv_it_value(itr, 0, 0)
    print('+++kv_it_value:', ret)
    assert ret == (0, 5, b'world')

    itr_ok, key_size, value_size = chain.kv_it_next(itr)
    print('+++kv_it_next:', itr_ok, key_size, value_size)
    assert itr_ok == 0
    ret = chain.kv_it_key(itr, 0, 0)
    print('+++kv_it_key:', ret)
    assert ret == (0, 6, b'helloo')

    ret = chain.kv_it_value(itr, 0, 0)
    print('+++kv_it_value:', ret)
    assert ret == (0, 6, b'worldd')

    ret = chain.kv_it_lower_bound(itr, 'hh')
    print('kv_it_lower_bound:', ret)
    assert ret == (-2, 0, 0)
