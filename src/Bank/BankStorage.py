

class BankStorageSingleton(object):
  
    users = {}
    cards = {}
    balances = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
          cls.instance = super(BankStorageSingleton, cls).__new__(cls)
        return cls.instance
   
    def newAccount(self,account:str,userFilePath:int):
        storage = BankStorageSingleton()
        if account not in storage.users.keys():
            storage.users[account] = userFilePath
        else:
            print(storage.users)
            return

    def getAccountBalance(self,account:str):
        storage = BankStorageSingleton()
        if account in storage.balances.keys():
            return storage.balances[account]
        else:
            return

    def addAccountBalance(self,account:str,balance:int):
        storage = BankStorageSingleton()
        if account in storage.balances.keys():
            storage.balances[account] += balance
        else:
            storage.balances[account] = balance

    def getCreditCardNumber(self,account:str):
        storage = BankStorageSingleton()
        if account in storage.cards.keys():
            return len(storage.cards[account])
        else:
            return 0
        
    def addCreditCard(self,account:str,cardPath:str, cardValue:int):
        storage = BankStorageSingleton()
        if account in storage.cards.keys():
            storage.cards[account].append((cardPath,cardValue))
        else:
            storage.cards[account] = [(cardPath,cardValue)]
