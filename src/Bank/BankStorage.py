

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

    def getCreditCardBalance(self,account:str,creditCardPath:str):
        storage = BankStorageSingleton()
        if account in storage.cards.keys():
            for (cpath, b , isActive) in storage.cards[account]:
                if(cpath  == creditCardPath and isActive == True):
                    return b
        return None

    def getCreditCardNumber(self,account:str):
        storage = BankStorageSingleton()
        if account in storage.cards.keys():
            return len(storage.cards[account])
        else:
            return 0
        
    def addCreditCard(self,account:str,cardPath:str, cardValue:int):
        storage = BankStorageSingleton()
        if account in storage.cards.keys():
            storage.cards[account].append((cardPath,cardValue,True))
        else:
            storage.cards[account] = [(cardPath,cardValue,True)]

    def updateCreditCardBalance(self,account:str,creditCardPath:str,balance:int):
        storage = BankStorageSingleton()
        storage.cards[account] = [(creditCardPath,balance,False) if item[0] == creditCardPath else item for item in storage.cards[account]]


    def isActiveCard(self, account: str,cardPath:str):
        storage = BankStorageSingleton()
        print(storage.cards[account])
        if account in storage.cards.keys():
            for (cpath, b , isActive) in storage.cards[account]:
                if(cpath == cardPath):
                    return isActive
        return False
    
    def areActiveCards(self, account: str):
        storage = BankStorageSingleton()
        if account in storage.cards.keys():
            for (cpath, b , isActive) in storage.cards[account]:
                if isActive:
                    return True
            return False
        return False
            