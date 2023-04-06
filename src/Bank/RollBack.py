import json
from BankStorage import *
from BankConnection import *

def RollBackEntry(Signedmessage,message,conn,privateKey,derived_key):

    if "OriginalMessageType" in message:
        match message["OriginalMessageType"]:
            case "NewAccount":
                response = rollBackNewAccountMode(Signedmessage,message)
                responseSigned = signedMessage(response,privateKey)
                sendMessage(conn,responseSigned,derived_key)
            case "Deposit":
                response = rollBackDepositMode(Signedmessage,message)
                responseSigned = signedMessage(response,privateKey)
                sendMessage(conn, responseSigned,derived_key)
            case "Balance":
                response = rollBackCreateCardMode(Signedmessage,message)
                responseSigned = signedMessage(response,privateKey)
                sendMessage(conn, responseSigned,derived_key)
            case "CreateCard":
                response = rollBackGetBalanceMode(Signedmessage,message)
                responseSigned = signedMessage(response,privateKey)
                sendMessage(conn,responseSigned,derived_key)
            case "WithdrawCard":
                response = rollBackWithdrawMode(Signedmessage,message)
                responseSigned = signedMessage(response,privateKey)
                sendMessage(conn,responseSigned,derived_key)

    return

def rollBackNewAccountMode(signedMessage, message):
    storage = BankStorageSingleton() 

    return


def rollBackDepositMode(signedMessage, message):
    storage = BankStorageSingleton()

    return


def rollBackCreateCardMode(signedMessage, message):
    storage = BankStorageSingleton()

    return


def rollBackGetBalanceMode(signedMessage, message):
    storage = BankStorageSingleton()

    return


def rollBackWithdrawMode(signedMessage, message):
    storage = BankStorageSingleton()

    return

