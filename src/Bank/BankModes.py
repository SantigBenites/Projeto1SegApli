import os, random, json, re
from BankStorage import *
from Cripto import *

current_working_directory = os.getcwd()

def newAccountMode(message):
    
    if "account" and "balance" and "fileName" and "content" not in message:
        return json.dumps({"Error":130}).encode('utf8')

    storage = BankStorageSingleton()
    accountName = message["account"]
    balance = message["balance"]
    userFileName = message["fileName"]
    userFileContent = message ["content"]

    # Checking user file doesn't exist
    if os.path.isfile(f"{current_working_directory}/src/Bank/users/{userFileName}"):
        return json.dumps({"Error":130}).encode('utf8')

    # Creating user file
    userPath = f"{current_working_directory}/src/Bank/users/{userFileName}"
    userFile = open(userPath, "a")
    userFile.write(userFileContent)
    userFile.close()
    
    h = hashFile(userPath)
    

    # Generating response
    newAccountResponse = json.dumps({
        "account":accountName,
        "initial_balance":balance
    }).encode('utf8')

    # Updating runtime database
    storage.newAccount(accountName,userPath,h)
    storage.addAccountBalance(accountName,balance)

    return newAccountResponse

def depositMode(message):
    
    if "account" and "Amount" and "file" not in message:
        return json.dumps({"Error":130}).encode('utf8')
    
    storage = BankStorageSingleton()
    account = message["account"]
    deposit = message["Amount"]
    hashFromUser = message["file"]
    
    ph = storage.getHashPathUser(account)
    
    if(ph == None):
        response = json.dumps({"Error":130}).encode('utf8')
        
    (path, hash) = ph
    
    
    #nedds to verify the userFile corresponds to account
    if(os.path.isfile(path)) and hash == hashFromUser:
        storage.addAccountBalance(account,deposit)
        response = json.dumps({"account":account, "deposit":deposit}).encode('utf8')
    else:
        response = json.dumps({"Error":130}).encode('utf8')

    return response

# Example: {"account":"55555","vcc_amount":12.00, "vcc_file":"55555_2.card"}
def createCardMode(message):
    
    if "account" and "amount" and "file" not in message:
        return json.dumps({"Error":130}).encode('utf8')

    storage = BankStorageSingleton()
    accountName = message["account"]
    amount = message["amount"]
    hashFromUser = message["file"]
    
    # Checking for account balance
    accountBalance = storage.getAccountBalance(accountName)
    if amount > accountBalance:
        return json.dumps({"Error":130}).encode('utf8')
    
    # Check for other active credit cards
    bool = storage.areActiveCards(accountName)
    if bool:
        return json.dumps({"Error":130}).encode('utf8')
    
    ph = storage.getHashPathUser(accountName)
    
    if(ph == None):
        return json.dumps({"Error":130}).encode('utf8')
    
    (path,hash) = ph
    
    if hash != hashFromUser:
        return json.dumps({"Error":130}).encode('utf8')
    
    
 
    # Getting card name
    numberOfCardForAccount = storage.getCreditCardNumber(accountName) + 1
    cardName = f"{accountName}_{numberOfCardForAccount}"

    # Creating credit card file
    cardPath = f"{current_working_directory}/src/Bank/creditCards/{cardName}.card"
    cardFile = open(cardPath, "a")
    cardFile.write(accountName)
    cardFile.close()

    # Generating response
    newCardResponse = json.dumps({
        "account":accountName,
        "vcc_amount":amount,
        "vcc_file": f"{cardName}.card"
    }).encode('utf8')

    # Updating runtime database
    storage.addCreditCard(accountName,cardPath,amount)

    return newCardResponse


def getBalanceMode(message):
    
    if "account" and "file" not in message:
        return json.dumps({"Error":130}).encode('utf8')
    
    account = message["account"]
    hashFromUser = message["file"]
    
    storage = BankStorageSingleton()
    
    ph = storage.getHashPathUser(account)
    
    if(ph == None):
        message = json.dumps({"Error":130})
        
    (pathFile,hash) = ph
    
    if os.path.isfile(pathFile) and hash == hashFromUser :
        response = json.dumps({"account": account, "balance": storage.getAccountBalance(account)})
        
    else:
        message = json.dumps({"Error":130})
    
    return response.encode('utf8')
    


def withdrawMode(message):
    
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

