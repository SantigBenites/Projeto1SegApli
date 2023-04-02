

class BankStorageSingleton(object):
  
    users = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
          cls.instance = super(BankStorageSingleton, cls).__new__(cls)
        return cls.instance
   
    def newAccount(self,account:str,balance:int):
        print("newAcount")
        storage = BankStorageSingleton()
        if account not in storage.users.keys():
            print(f"new account {account}:{balance}")
            storage.users[account] = balance
            print(storage.users)
        else:
            print(storage.users)
            return
        
    def deposite(self,account:str, deposit: int):
        print("deposit")
        storage = BankStorageSingleton()
        print(storage.users)
        if account in storage.users.keys():
            storage.users[account] = storage.users[account] + deposit
            print(storage.users)
            return 1
        return -1
            
        
