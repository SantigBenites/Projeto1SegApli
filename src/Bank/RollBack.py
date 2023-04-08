import json
from BankStorage import *
from BankConnection import *
from utils import *

def rollBackNewAccountMode(signedMessage, message, PublicKeyUser):

    if "account" not in message or "balance" not in message:
        return json.dumps({"Error":130}).encode('utf8')
        
    #Authentication
    if not verifySignature(PublicKeyUser,signedMessage["signature"],signedMessage["message"]):
        return json.dumps({"Error":130}).encode('utf8')

    # Start Storage Singleton
    storage = BankStorageSingleton()
    accountName = message["account"]
    balance = message["balance"]

    # Verify message parameters are valid
    if  not (
            argsAreValidAccountNames(str(accountName)) and
            argsAreValidBalances(str(balance))):
                
                return json.dumps({"Error":130}).encode('utf8')
    
    # Updating runtime database
    print(f"Before rollBack \n {storage.users} \n {storage.balances}")
    storage.removeAccount(accountName,PublicKeyUser)
    storage.addAccountBalance(accountName,-balance)
    print(f"Before rollBack \n {storage.users} \n {storage.balances}")
    return


def rollBackDepositMode(signedMessage, message):
    
    print("Started Rollback")
    if "account" not in message or "Amount" not in message:
        return  json.dumps({"Error":130}).encode('utf8')

    storage = BankStorageSingleton()
    account = message["account"]
    deposit = message["Amount"]

    # Verify message parameters are valid
    if  not (
        argsAreValidAccountNames(str(account)) and
        argsAreValidBalances(str(deposit))):
            
            return json.dumps({"Error":130}).encode('utf8')
    
    PublicKeyUser = storage.getPublicKeyUser(account)
    
    if(PublicKeyUser == None):
        return json.dumps({"Error":130}).encode('utf8')
        
    
    #Authentication
    if not verifySignature(PublicKeyUser,signedMessage["signature"],signedMessage["message"]):
        return json.dumps({"Error":130}).encode('utf8')
    
    print(f"Before rollBack \n {storage.balances}")
    storage.addAccountBalance(account,-deposit)
    print(f"After rollBack \n {storage.balances}")

    return


def rollBackCreateCardMode(signedMessage, message):
    
    # Start Singletion
    storage = BankStorageSingleton()

    # Checks for message keys and obtain values
    if "account" not in message or "amount" not in message:
        return json.dumps({"Error":130}).encode('utf8')

    storage = BankStorageSingleton()
    accountName = message["account"]
    amount = message["amount"]

    # Verify message parameters are valid
    if  not (
        argsAreValidAccountNames(str(accountName)) and
        argsAreValidBalances(str(amount))):
            
            return json.dumps({"Error":130}).encode('utf8')
    
    PublickeyUser = storage.getPublicKeyUser(accountName)
    
    if(PublickeyUser == None):
        return json.dumps({"Error":130}).encode('utf8')
    
    if not verifySignature(PublickeyUser,signedMessage["signature"],signedMessage["message"]):
         return json.dumps({"Error":130}).encode('utf8')
    # Getting card name
    numberOfCardForAccount = storage.getCreditCardNumber(accountName)
    cardName = f"{accountName}_{numberOfCardForAccount}"
    print(f"Before rollBack \n {storage.cards}")
    storage.removeCreditCard(accountName,f"{cardName}.card")
    print(f"Before rollBack \n {storage.cards}")
    return


def rollBackGetBalanceMode(signedMessage, message):
    storage = BankStorageSingleton()
    # No need becuase it cant be used
    return


def rollBackWithdrawMode(signedMessage, message,privateKey,PublicKeyStore):

    #verifies signature of store
    if not verifySignature(PublicKeyStore,signedMessage["signature"],signedMessage["message"]):
        return json.dumps({"Error":131}).encode('utf8')
    
    if "contentFile" not in message or "ShoppingValue" not in message:
        return json.dumps({"Error":132}).encode('utf8')
    
    fileContent = message["contentFile"]
    
    decriptedData =  decryptWithPrivateKey(privateKey, fileContent["message"])
    
    storage = BankStorageSingleton()
    
    msg = json.loads(decriptedData)
    if "account" not  in msg or "vcc_amount" not  in msg or "vcc_file" not  in msg:
        return json.dumps({"Error":133}).encode('utf8')
    
    # Get message values
    account = msg["account"] 
    vcc_amount = msg["vcc_amount"]
    vcc_file = msg["vcc_file"]
    shoppingValue = message["ShoppingValue"]

    # All Validation for all inputs
    # Validate with regex
    if  not (
        argsAreValidAccountNames(str(account)) and
        argsAreValidBalances(str(vcc_amount)) and 
        argsAreValidFileNames(str(vcc_file)) and 
        argsAreValidBalances(str(shoppingValue))):
            return 135
    
    PublicKeyClient = storage.getPublicKeyUser(account)
    
    if PublicKeyClient == None:
        return json.dumps({"Error":136}).encode('utf8')
    
    #verify signatures
    if not verifySignature(PublicKeyClient,fileContent["signature"],fileContent["message"]):
        return json.dumps({"Error":137}).encode('utf8')


    if shoppingValue < 0 :
        return json.dumps({"Error":138}).encode('utf8')

    bool = storage.isActiveCard(account,vcc_file)
    
    if bool:
        return json.dumps({"Error":139}).encode('utf8')

    amount = storage.getUsedCreditCardBalance(account,vcc_file)

    if(amount+shoppingValue != vcc_amount):
        return json.dumps({"Error":140}).encode('utf8')

    # Check if credit card as the required amount
    print(f"Before rollBack \n {storage.cards} \n {storage.balances}")
    storage.reactivateCreditCardAndUpdateBalance(account,vcc_file, amount+shoppingValue)
    storage.addAccountBalance(account,+shoppingValue)
    print(f"Before rollBack \n {storage.cards} \n {storage.balances}")
    
    return

