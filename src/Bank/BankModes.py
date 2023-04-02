import os, random, json
from BankStorage import *

current_working_directory = os.getcwd()

def newAccountMode(message):

    storage = BankStorageSingleton()
    accountName = message["account"]
    balance = message["balance"]

    if os.path.isfile(f"{current_working_directory}/src/Bank/users/{accountName}.user"):
        return json.dumps({"Error":130}).encode('utf8')

    userPath = f"{current_working_directory}/src/Bank/users/{accountName}.user"
    userFile = open(userPath, "a")
    userFile.close()

    newAccountResponse = json.dumps({
        "account":accountName,
        "initial_balance":balance
    }).encode('utf8')

    storage.newAccount(accountName,userPath)

    return newAccountResponse


def depositMode():
    return


def createCardMode():
    return


def getBalanceMode():
    return


def withrawMode():
    return

