import os, random, json, re
from BankStorage import *

current_working_directory = os.getcwd()

def newAccountMode(message):

    storage = BankStorageSingleton()
    accountName = message["account"]
    balance = message["balance"]

    # Checking user file doesn't exist
    if os.path.isfile(f"{current_working_directory}/src/Bank/users/{accountName}.user"):
        return json.dumps({"Error":130}).encode('utf8')

    # Creating user file
    userPath = f"{current_working_directory}/src/Bank/users/{accountName}.user"
    userFile = open(userPath, "a")
    userFile.close()

    # Generating response
    newAccountResponse = json.dumps({
        "account":accountName,
        "initial_balance":balance
    }).encode('utf8')

    # Updating runtime database
    storage.newAccount(accountName,userPath)
    storage.addAccountBalance(accountName,balance)

    return newAccountResponse

def depositMode(message):
    
    storage = BankStorageSingleton()
    account = message["account"]
    deposit = message["Amount"]
    
    #nedds to verify the userFile corresponds to account
    if(os.path.isfile(f"{current_working_directory}/src/Bank/users/{account}.user")):
        storage.addAccountBalance(account,deposit)
        response = json.dumps({"account":account, "balance":storage.getAccountBalance(account)}).encode('utf8')
    else:
        response = json.dumps({"Error":130}).encode('utf8')

    return response

# Example: {"account":"55555","vcc_amount":12.00, "vcc_file":"55555_2.card"}
def createCardMode(message):

    storage = BankStorageSingleton()
    accountName = message["account"]
    amount = message["amount"]

    # Checking for already existing credit cards
    creditCards = os.listdir(f"{current_working_directory}/src/Bank/creditCards")
    r = re.compile("55555_\d+.card")
    matches = list(filter(r.match, creditCards))
    if len(matches) > 0:
        return json.dumps({"Error":130}).encode('utf8')
    
    # Checking for account balance
    accountBalance = storage.getAccountBalance(accountName)
    if amount > accountBalance:
        return json.dumps({"Error":130}).encode('utf8')
    
    # Check for other active credit cards

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
    
    account = message["account"]
    
    storage = BankStorageSingleton()
    
    response = json.dumps({"account": account, "balance": storage.getAccountBalance(account)})
    
    return response.encode('utf8')
    


def withdrawMode(message):
    print("wMode")
    #print(message)
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
        return json.dumps({"Error":130}).encode('utf8')

    # Check if credit card as the required amount
    
    accountInput = virtualCreditCardFile.split('_')[0]
    
    
    #print(storage.getCreditCardNumber(account))
    (path,amount) = storage.getCreditCardBalance(account,cardPath)[0]


    print(account == accountInput)
    print(amount >= shoppingValue)
    
    
    if account == accountInput and amount >= shoppingValue:
        storage.updateCreditCardBalance(account,cardPath, amount-shoppingValue)
        storage.addAccountBalance(account,-shoppingValue)
        message = json.dumps({"vcc_file": virtualCreditCardFile , "vcc_amount_used": shoppingValue})

    else:
        message = json.dumps({"Error":130})
        
    # Remove 
    print(message)
    return message.encode('utf8')

