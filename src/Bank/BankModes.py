import os, random, json
from BankStorage import *

current_working_directory = os.getcwd()

def newAccountMode(message):

    storage = BankStorageSingleton()
    accountName = message["account"]
    balance = message["balance"]

    if os.path.isfile(f"{current_working_directory}/src/Bank/users/{accountName}.user"):
        return json.dumps({ "MessageType":1}).encode('utf8')

    PIN = random.randrange(99999,999999)
    userFile = open(f"{current_working_directory}/src/Bank/users/{accountName}.user", "wb")
    userFile.write(f"{accountName}:{PIN}".encode('utf8'))
    userFile.close()

    newAccountReponse = json.dumps({
        "MessageType":0,
        "PIN":PIN
    }).encode('utf8')

    storage.newAccount(accountName,balance)

    return newAccountReponse


def depositMode(message):
    
    storage = BankStorageSingleton()
    account = message["account"]
    deposit = message["Amount"]
    userFile = message["userFile"]
    
    #nedds to verify the userFile corresponds to account
    if(os.path.isfile(f"{current_working_directory}/src/Bank/users/{userFile}")):
        r = storage.deposite(account,deposit)
        if(r == -1):
            response = json.dumps({ "MessageType":-1}).encode('utf8')
        response = json.dumps({"MessageType": 0}).encode('utf8')
        
    else:
        response = json.dumps({ "MessageType":-1}).encode('utf8')
    
    return response


def createCardMode():
    return


def getBalanceMode():
    return


def withrawMode():
    return

