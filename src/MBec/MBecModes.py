import sys, socket, json, os
from utils import safe_execute
from MBecConnection import sendMessage

current_working_directory = os.getcwd()

def newAccountMode(argv:list[str]):


    account = argv[argv.index("-a")+1] if "-a" in argv else sys.exit(0)
    authFile = argv[argv.index("-s")+1] if "-s" in argv else "bank.auth"
    ipBankAddress = argv[argv.index("-i")+1] if "-i" in argv else "127.0.0.1"
    portStr = argv[argv.index("-p")+1] if "-p" in argv else 3000
    bkPort = int(portStr) if safe_execute(0,TypeError,int,portStr) != 0 else 3000
    userFile = argv[argv.index("-u")+1] if "-u" in argv else f"{account}.user"
    balanceStr = argv[argv.index("-n")+1] if "-n" in argv else sys.exit(1)
    balance = int(balanceStr) if safe_execute(0,TypeError,int,balanceStr) != 0 else sys.exit(1)

    if balance < 15:
        return
    
    newAccountMessage = json.dumps({
        "MessageType": "NewAccount",
        "account": account,
        "balance": balance,
    }).encode('utf8')

    messageEncode = sendMessage(ipBankAddress,bkPort,newAccountMessage)
    returnMessage = json.loads(messageEncode.decode('utf8'))
    if "account" in returnMessage and "initial_balance" in returnMessage:
        userFile = open(f"{current_working_directory}/src/MBec/usersFiles/{userFile}", "a")
        userFile.close()

        return returnMessage
    else:
        print(f"Error num {returnMessage['Error']}")
        sys.exit(1)



def depositMode(argv:list[str]):
    
    account = argv[argv.index("-a")+1] if "-a" in argv else exit(1)
    # it must be the same file produced by mbec when the account was created
    userFile = argv[argv.index("-u") + 1] if "-u" in argv else f"{account}.user"
    ipBankAddress = argv[argv.index("-i") + 1] if "-i" in argv else "127.0.0.1"
    bkPort = int(argv[argv.index("-p") + 1]) if "-p" in argv else 3000
    authFile = argv[argv.index("-s") + 1] if "-s" in argv else "bank.auth"
    amount = int(argv[argv.index("-d") + 1]) if "-d" in argv else exit(1)
    
    if(amount <= 0): 
        print ("Invalid Amount") 
        exit (1)


    m = json.dumps({"MessageType": "Deposit", "Amount":amount, "account":account})
    print(m)
    
    receivedMessage = json.loads(sendMessage(ipBankAddress,bkPort,m.encode('utf8')).decode('utf8'))
    print(receivedMessage)
    
    if "account" in receivedMessage and "balance" in receivedMessage:
        return receivedMessage
        
    else:
        print("Error")
        exit(1)
    return


# mbec [-s <auth-file>] [-i <ip-bank-address>] [-p <bk-port>] [-u <user-file>] -a <account> -c <amount>
def createCardMode(argv:list[str]):

    authFile = argv[argv.index("-s")+1] if "-s" in argv else "bank.auth"
    ipBankAddress = argv[argv.index("-i")+1] if "-i" in argv else "127.0.0.1"
    portStr = argv[argv.index("-p")+1] if "-p" in argv else 3000
    bkPort = int(portStr) if safe_execute(0,TypeError,int,portStr) != 0 else 3000
    account = argv[argv.index("-a")+1] if "-a" in argv else sys.exit(0)
    userFile = argv[argv.index("-u")+1] if "-u" in argv else f"{account}.auth"
    amountStr = argv[argv.index("-c")+1] if "-c" in argv else sys.exit(1)
    amount = int(amountStr) if safe_execute(0,TypeError,int,amountStr) != 0 else sys.exit(1)

    if not os.path.isfile(f"{current_working_directory}/src/MBec/usersFiles/{userFile}"):
        print(f"Error num 130")
        sys.exit(1)

    if amount <= 0:
        print(f"Error num 130")
        sys.exit(1)

    newCardMessage = json.dumps({
        "MessageType": "CreateCard",
        "account": account,
        "amount": amount,
    }).encode('utf8')

    messageEncode = sendMessage(ipBankAddress,bkPort,newCardMessage)
    returnMessage = json.loads(messageEncode.decode('utf8'))
    if "account" and "vcc_amount" and "vcc_file" in returnMessage:
        return returnMessage
    else:
        print(f"Error num {returnMessage['Error']}")
        sys.exit(1)

    return


# mbec [-s <auth-file>] [-i <ip-bank-address>] [-p <bk-port>] [-u <user-file>] -a <account> -g
def getBalanceMode(argv:list[str]):
    
    account = argv[argv.index("-a")+1] if "-a" in argv else exit(1)
    # it must be the same file produced by mbec when the account was created
    userFile = argv[argv.index("-u") + 1] if "-u" in argv else f"{account}.user"
    ipBankAddress = argv[argv.index("-i") + 1] if "-i" in argv else "127.0.0.1"
    bkPort = int(argv[argv.index("-p") + 1]) if "-p" in argv else 3000
    authFile = argv[argv.index("-s") + 1] if "-s" in argv else "bank.auth"
    
    m = json.dumps({"MessageType": "Balance", "account":account})
    
    receivedMessage = json.loads(sendMessage(ipBankAddress,bkPort,m.encode('utf8')).decode('utf8'))
    
    if "account" in receivedMessage and "balance" in receivedMessage:
        return receivedMessage
    else:
        print("Error")
        exit(1)




def withrawMode():
    return
