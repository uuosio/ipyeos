import time
from pyeoskit import eosapi, wallet
wallet.import_key('test', '5JRYimgLBrRLCBAcjHUWCYRv3asNedTYYzVgmiU4q2ZVxMBiJXL')
wallet.import_key('test', '5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3')

eosapi.set_node('http://127.0.0.1:9000')
# print(eosapi.get_account('hello'))
old_balance = eosapi.get_balance('eosio')
print(old_balance)
print(eosapi.timeout)
eosapi.timeout = 100
eosapi.transfer('eosio', 'eosio.token', 0.0001, 'hello')
for i in range(10):
    new_balance = eosapi.get_balance('eosio')
    print(new_balance)
    if new_balance != old_balance:
        break
    time.sleep(3.0)
