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

def depositMode():
    return

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

    # Getting card name
    numberOfCardForAccount = storage.getCreditCardNumber(accountName) + 1
    cardName = f"{accountName}_{numberOfCardForAccount}"

    # Creating credit card file
    cardPath = f"{current_working_directory}/src/Bank/creditCards/{cardName}.card"
    cardFile = open(cardPath, "a")
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


def getBalanceMode():
    return


def withrawMode():
    return

