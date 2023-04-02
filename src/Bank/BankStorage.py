

class BankStorageSingleton(object):
  
    users = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
          cls.instance = super(BankStorageSingleton, cls).__new__(cls)
        return cls.instance
   
    def newAccount(self,account:str,userFilePath:int):
        storage = BankStorageSingleton()
        if account not in storage.users.keys():
            storage.users[account] = userFilePath
        else:
            return
