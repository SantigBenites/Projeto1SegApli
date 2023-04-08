import json
from BankStorage import *
from BankConnection import *
from utils import *

def RollBackEntry(Signedmessage,message):

    if "OriginalMessageType" in message:
        match message["OriginalMessageType"]:
            case "NewAccount":
                response = rollBackNewAccountMode(Signedmessage,message)
            case "Deposit":
                response = rollBackDepositMode(Signedmessage,message)
            case "CreateCard":
                response = rollBackCreateCardMode(Signedmessage,message)
            case "Balance":
                response = rollBackGetBalanceMode(Signedmessage,message)
            case "WithdrawCard":
                response = rollBackWithdrawMode(Signedmessage,message)

    return

def rollBackNewAccountMode(signedMessage, message):
    storage = BankStorageSingleton() 
    # No need becuase it cant be used
    return


def rollBackDepositMode(signedMessage, message):
    storage = BankStorageSingleton()
    # No need becuase it cant be used 
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

    storage.removeCreditCard(accountName,f"{cardName}.card")

    return


def rollBackGetBalanceMode(signedMessage, message):
    storage = BankStorageSingleton()
    # No need becuase it cant be used
    return


def rollBackWithdrawMode(signedMessage, message):
    storage = BankStorageSingleton()
    # No need becuase it cant be used
    return

