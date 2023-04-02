

class BankStorageSingleton(object):
  
    users = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
          cls.instance = super(BankStorageSingleton, cls).__new__(cls)
        return cls.instance
   
    def newAccount(self,account:str,balance:int):
        storage = BankStorageSingleton()
        if account not in storage.users.keys():
            print(f"new account {account}:{balance}")
            storage.users[account] = balance
        else:
            return
