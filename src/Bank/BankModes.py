import os, random, json

current_working_directory = os.getcwd()

def newAccountMode(message):

    accountName = message["account"]
    balance = message["balance"]
    if os.path.isfile(f"users/{accountName}.user"):
        return json.dumps({ "MessageType":1}).encode('utf8')

    PIN = random.randrange(99999,999999)
    userFile = open(f"{current_working_directory}/src/Bank/users/{accountName}.user", "a")
    userFile.write(f"{accountName}:{PIN}")
    userFile.close()

    newAccountReponse = json.dumps({
        "MessageType":0,
        "PIN":PIN
    }).encode('utf8')

    return newAccountReponse


def depositMode():
    return


def createCardMode():
    return


def getBalanceMode():
    return


def withrawMode():
    return

