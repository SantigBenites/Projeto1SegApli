import os, random, json, re, time
import pickle
import secrets
import socket
from BankStorage import *
from Cripto import *
from Authentication import *
from utils import *

current_working_directory = os.getcwd()

def newAccountMode(signedMessage, message,PublicKeyUser):
    
    if "account" not in message or "balance" not in message or "timeStamp" not in message:
        return json.dumps({"Error":130}).encode('utf8')
        
    #Authentication
    if not verifySignature(PublicKeyUser,signedMessage["signature"],signedMessage["message"]):
        return json.dumps({"Error":130}).encode('utf8')

    # Start Storage Singleton
    storage = BankStorageSingleton()
    accountName = message["account"]
    balance = message["balance"]
    timeStampClient = message["timeStamp"]


    # Verify message parameters are valid
    if  not (
            argsAreValidAccountNames(str(accountName)) and
            argsAreValidBalances(str(balance)) and
            verifyTimeStampValidity(timeStampClient)):
                return json.dumps({"Error":130}).encode('utf8')

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
    
    if "account" not in message or "Amount" not in message or "timeStamp" not in message:
        return  json.dumps({"Error":130}).encode('utf8')

    storage = BankStorageSingleton()
    account = message["account"]
    deposit = message["Amount"]
    timeStampClient = message["timeStamp"]

    # Verify message parameters are valid
    if  not (
        argsAreValidAccountNames(str(account)) and
        argsAreValidBalances(str(deposit)) and
        verifyTimeStampValidity(timeStampClient)):
            
            return json.dumps({"Error":130}).encode('utf8')
    
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
    
    if "account" not in message or "amount" not in message or "timeStamp" not in message:
        return json.dumps({"Error":130}).encode('utf8')

    storage = BankStorageSingleton()
    accountName = message["account"]
    amount = message["amount"]
    timeStampClient = message["timeStamp"]


    # Verify message parameters are valid
    if  not (
        argsAreValidAccountNames(str(accountName)) and
        argsAreValidBalances(str(amount)) and
        verifyTimeStampValidity(timeStampClient)
        ):
            
            return json.dumps({"Error":130}).encode('utf8')
    
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
    storage.addCreditCard(accountName,f"{cardName}.card",amount)
    
    return newCardResponse


def getBalanceMode(signedMessage, message):
    
    if "account" not in message or "timeStamp" not in message:
        return json.dumps({"Error":130}).encode('utf8')
    
    account = message["account"]
    timeStampClient = message["timeStamp"]

    # Verify message parameters are valid
    if  not (
        argsAreValidAccountNames(str(account)) and
        verifyTimeStampValidity(timeStampClient)
        ):
            
            return json.dumps({"Error":130}).encode('utf8')
    
    storage = BankStorageSingleton()
    
    publicKeyUser = storage.getPublicKeyUser(account)
    
    if(publicKeyUser == None):
        return json.dumps({"Error":130}).encode('utf8')
        
    if not verifySignature(publicKeyUser,signedMessage["signature"],signedMessage["message"]):
        return json.dumps({"Error":130}).encode('utf8')
     
    response = json.dumps({"account": account, "balance": storage.getAccountBalance(account)})
        
    return response.encode('utf8')
    


def withdrawMode(signedMessage, message,privateKey,PublicKeyStore):
    
    #verifies signature of store
    if not verifySignature(PublicKeyStore,signedMessage["signature"],signedMessage["message"]):
        return json.dumps({"Error":130}).encode('utf8')

    
    if "contentFile" not in message or "ShoppingValue" not in message or "IPClient" not in message or "portClient" not in message:
        return json.dumps({"Error":130}).encode('utf8')
    
    fileContent = message["contentFile"]
    
    decriptedData =  decryptWithPrivateKey(privateKey, fileContent["message"])
    
    storage = BankStorageSingleton()
    
    msg = json.loads(decriptedData)
    if "account" not  in msg or "vcc_amount" not  in msg or "vcc_file" not  in msg:
        return json.dumps({"Error":130}).encode('utf8')
    
    # Get message values
    account = msg["account"] 
    vcc_amount = msg["vcc_amount"]
    vcc_file = msg["vcc_file"]
    shoppingValue = message["ShoppingValue"]
    userIP = message["IPClient"]
    userPort = message["portClient"]
    timeStampClient = message["timeStamp"]

    # All Validation for all inputs
    # Validate port is int
    if safe_execute("error",TypeError,int,userPort) != "error":
        userPort = int(userPort)
    else:
        return 130
    # Validate with regex
    if  not (
        argsAreValidAccountNames(str(account)) and
        argsAreValidIPv4(str(userIP)) and
        argsAreValidPort(userPort) and 
        argsAreValidBalances(str(vcc_amount)) and 
        argsAreValidFileNames(str(vcc_file)) and 
        argsAreValidBalances(str(shoppingValue)) and
        verifyTimeStampValidity(timeStampClient)):
            return 130
    
    PublicKeyClient = storage.getPublicKeyUser(account)
    
    if PublicKeyClient == None:
        return json.dumps({"Error":130}).encode('utf8')
    
    #verify signatures
    if not verifySignature(PublicKeyClient,fileContent["signature"],fileContent["message"]):
        return json.dumps({"Error":130}).encode('utf8')


    if shoppingValue < 0 :
        return json.dumps({"Error":132}).encode('utf8')

    bool = storage.isActiveCard(account,vcc_file)
    
    if not bool:
        return json.dumps({"Error":133}).encode('utf8')

    amount = storage.getCreditCardBalance(account,vcc_file)
    
    if(amount != vcc_amount):
        return json.dumps({"Error":130}).encode('utf8')

    # Get Hash of file
    fileHash = hashlib.sha256(pickle.dumps(message)).hexdigest()
    clientResponse = ClientMode(userIP,int(userPort),fileHash)

    # Check if the client socket timed out
    if clientResponse == None:
        return json.dumps({"Error":130}).encode('utf8') 

    # Check if credit card as the required amount
    if amount >= shoppingValue:
        storage.updateCreditCardBalance(account,vcc_file, amount-shoppingValue)
        storage.addAccountBalance(account,-shoppingValue)
        message = json.dumps({"vcc_file": vcc_file , "vcc_amount_used": shoppingValue})

    else:
        message = json.dumps({"Error":134})
        
    return message.encode('utf8')

