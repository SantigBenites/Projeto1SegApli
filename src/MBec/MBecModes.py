import sys, socket
from utils import safe_execute
from MBecConnection import sendMessage
import json

def newAccountMode(argv:list[str]):


    accountStr = argv[argv.index("-a")+1] if "-a" in argv else sys.exit(0)
    account = int(accountStr) if safe_execute(0,TypeError,int,accountStr) != 0 else sys.exit(0)
    authFile = argv[argv.index("-s")+1] if "-s" in argv else "bank.auth"
    ipBankAddress = argv[argv.index("-i")+1] if "-i" in argv else "127.0.0.1"
    portStr = argv[argv.index("-p")+1] if "-p" in argv else 3000
    bkPort = int(portStr) if safe_execute(0,TypeError,int,portStr) != 0 else 3000
    userFile = argv[argv.index("-u")+1] if "-u" in argv else f"{account}.auth"
    balance = argv[argv.index("-n")+1] if "-n" in argv else sys.exit(1)
    
    newAccountMessage = json.dumps({
        "MessageType": "NewAccount",
        "account": account,
        "balance": balance,
    }).encode('utf8')

    messageEncode = sendMessage(ipBankAddress,bkPort,newAccountMessage)
    returnMessage = json.loads(messageEncode.decode('utf8'))
    if returnMessage["MessageType"] == 0:
        userFile = open(f"usersFiles/{userFile}", "a")
        PIN = returnMessage["PIN"]
        userFile.write(f"{account}:{PIN}")
        userFile.close()
        return
    else:
        sys.exit(1)



def depositMode():
    return



def createCardMode():
    return



def getBalanceMode():
    return



def withrawMode():
    return
