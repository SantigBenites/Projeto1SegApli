import os, random, json, re
import pickle
import secrets
import socket
from BankStorage import *
from Cripto import *
from Authentication import *

current_working_directory = os.getcwd()

def newAccountMode(signedMessage, message):
    
    if "account" and "balance" and "publicKey" not in message:
        return json.dumps({"Error":130}).encode('utf8')
        
    
    PublicKeyUser = serialization.load_pem_public_key(
        message["publicKey"].encode()
    )
    
    #Authentication
    if not verifySignature(PublicKeyUser,signedMessage["signature"],signedMessage["message"]):
         return json.dumps({"Error":130}).encode('utf8')


    storage = BankStorageSingleton()
    accountName = message["account"]
    balance = message["balance"]

    # Generating response
    newAccountResponse = json.dumps({
        "account":accountName,
        "initial_balance":balance
    }).encode('utf8')

    # Updating runtime database
    storage.newAccount(accountName,PublicKeyUser)
    storage.addAccountBalance(accountName,balance)

    return newAccountResponse

def depositMode(signedMessage, message):
    
    if "account" and "Amount" not in message:
        return  json.dumps({"Error":130}).encode('utf8')

    storage = BankStorageSingleton()
    account = message["account"]
    deposit = message["Amount"]
    
    PublicKeyUser = storage.getPublicKeyUser(account)
    
    if(PublicKeyUser == None):
        return json.dumps({"Error":130}).encode('utf8')
        
    
    #Authentication
    if not verifySignature(PublicKeyUser,signedMessage["signature"],signedMessage["message"]):
        return json.dumps({"Error":130}).encode('utf8')
    
    storage.addAccountBalance(account,deposit)
    

    response = json.dumps({"account":account, "deposit":deposit}).encode('utf8')

    return response

# Example: {"account":"55555","vcc_amount":12.00, "vcc_file":"55555_2.card"}
def createCardMode(signedMessage, message):
    
    if "account" and "amount" not in message:
        return json.dumps({"Error":130}).encode('utf8')

    storage = BankStorageSingleton()
    accountName = message["account"]
    amount = message["amount"]
    
    PublickeyUser = storage.getPublicKeyUser(accountName)
    
    if(PublickeyUser == None):
        return json.dumps({"Error":130}).encode('utf8')

    
    # Checking for account balance
    accountBalance = storage.getAccountBalance(accountName)
    if amount > accountBalance:
        return json.dumps({"Error":130}).encode('utf8')
    # Check for other active credit cards
    bool = storage.areActiveCards(accountName)
    if bool:
        return json.dumps({"Error":130}).encode('utf8')
    

    if not verifySignature(PublickeyUser,signedMessage["signature"],signedMessage["message"]):
         return json.dumps({"Error":130}).encode('utf8')
    # Getting card name
    numberOfCardForAccount = storage.getCreditCardNumber(accountName) + 1
    cardName = f"{accountName}_{numberOfCardForAccount}"
    
    #criar dados e enviar para mbec

    # Generating response
    newCardResponse = json.dumps({
        "account":accountName,
        "vcc_amount":amount,
        "vcc_file": f"{cardName}.card"
    }).encode('utf8')

    # Updating runtime database
    storage.addCreditCard(accountName,cardName,amount)
    
    return newCardResponse


def getBalanceMode(signedMessage, message):
    
    if "account"  not in message:
        return json.dumps({"Error":130}).encode('utf8')
    
    account = message["account"]
    
    storage = BankStorageSingleton()
    
    publicKeyUser = storage.getPublicKeyUser(account)
    
    if(publicKeyUser == None):
        return json.dumps({"Error":130}).encode('utf8')
        
    if not verifySignature(publicKeyUser,signedMessage["signature"],signedMessage["message"]):
        return json.dumps({"Error":130}).encode('utf8')
     
    response = json.dumps({"account": account, "balance": storage.getAccountBalance(account)})
        
    return response.encode('utf8')
    


def withdrawMode(signedMessage, message):
    
    if "CreditCardFile" and "ShoppingValue" not in message:
        return json.dumps({"Error":130}).encode('utf8')

    # Get message values
    virtualCreditCardFile = message["CreditCardFile"]
    shoppingValue = message["ShoppingValue"]
    storage = BankStorageSingleton()

    # Get account from credit card file
    if os.path.isfile(f"{current_working_directory}/src/Bank/creditCards/{virtualCreditCardFile}"):
        cardPath = f"{current_working_directory}/src/Bank/creditCards/{virtualCreditCardFile}"
        f = open(cardPath, "r")
        account =f.read()
    else:
        return json.dumps({"Error":131}).encode('utf8')

    if shoppingValue < 0 :
        return json.dumps({"Error":132}).encode('utf8')
    
    
    bool = storage.isActiveCard(account,cardPath)
    
    if not bool:
        return json.dumps({"Error":133}).encode('utf8')

    amount = storage.getCreditCardBalance(account,cardPath)
    
    # Check if credit card as the required amount
    if amount >= shoppingValue:
        storage.updateCreditCardBalance(account,cardPath, amount-shoppingValue)
        storage.addAccountBalance(account,-shoppingValue)
        message = json.dumps({"vcc_file": virtualCreditCardFile , "vcc_amount_used": shoppingValue})

    else:
        message = json.dumps({"Error":134})
        
    return message.encode('utf8')

