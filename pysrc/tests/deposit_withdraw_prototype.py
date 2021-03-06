
class Blockchain:
    def __init__(self, total_supply):
        self.total_supply = total_supply
        self.accounts = {'master': total_supply}

    def create_account(self, name):
        self.accounts[name] = 0

    def issue(self, account, amount):
        assert self.accounts['master'] >= amount
        self.accounts['master'] -= amount
        self.accounts[account] += amount

    def transfer(self, _from, _to, amount):
        assert self.accounts[_from] >= amount
        self.accounts[_from] -= amount
        self.accounts[_to] += amount

class MixinNetwork(Blockchain):
    pass

class EOSNetwork(Blockchain):
    pass

class Test:
    def __init__(self):
        self.mixin = MixinNetwork(10000)
        self.eos = EOSNetwork(10000)

        self.mixin.create_account('alice')
        self.mixin.create_account('bob')

        self.eos.create_account('alice')
        self.eos.create_account('bob')

        self.mixin.issue('alice', 10)
        self.mixin.issue('bob', 10)

    def deposit(self, account, amount):
        success = self.mixin.transfer(account, 'master', amount)
        if not success:
            return

        success = self.eos.transfer('master', account, amount)
        if not success:
            self.mixin.transfer('master', account, amount) # refund

    def withdraw(self, account, amount):
        success = self.eos.transfer(account, 'master', amount)
        if not success:
            return

        success = self.mixin.transfer('master', account, amount):
        if not success:
            self.eos.transfer('master', account, amount) #refund
