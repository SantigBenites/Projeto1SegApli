import sys, socket, json, os
from utils import safe_execute
from MBecConnection import sendMessage

current_working_directory = os.getcwd()

def newAccountMode(argv:list[str]):

    # Verify if account is in argv
    if "-a" in argv:
        account = argv[argv.index("-a")+1]
    else: 
        return 130
    
    # Terminal line inputs
    authFile = argv[argv.index("-s")+1] if "-s" in argv else "bank.auth"
    ipBankAddress = argv[argv.index("-i")+1] if "-i" in argv else "127.0.0.1"
    portStr = argv[argv.index("-p")+1] if "-p" in argv else 3000
    bkPort = int(portStr) if safe_execute("error",TypeError,int,portStr) != "error" else 3000
    userFile = argv[argv.index("-u")+1] if "-u" in argv else f"{account}.user"
    
    # Verify if balance is in argv and if is a int
    if "-n" in argv and safe_execute("error",TypeError,float,argv[argv.index("-n")+1]) != "error":
        balance = float(argv[argv.index("-n")+1])
    else:
        return 130

    # Check if initial balance is above 15
    if balance < 15:
        return 130

    # Generate message
    newAccountMessage = json.dumps({
        "MessageType": "NewAccount",
        "account": account,
        "balance": balance,
    }).encode('utf8')

    # Send receive message from Bank
    messageEncode = sendMessage(ipBankAddress,bkPort,newAccountMessage)
    returnMessage = json.loads(messageEncode.decode('utf8'))

    # Check if Bank response is valid or Error 
    if "account" in returnMessage and "initial_balance" in returnMessage:

        # Create user file
        userFile = open(f"{current_working_directory}/src/MBec/usersFiles/{userFile}", "a")
        userFile.close()

        return returnMessage
    else:

        # Error from Bank
        return 130



def depositMode(argv:list[str]):
    
    # Verify if account is in argv
    if "-a" in argv:
        account = argv[argv.index("-a")+1]
    else: 
        return 130
    
    # it must be the same file produced by mbec when the account was created
    userFile = argv[argv.index("-u") + 1] if "-u" in argv else f"{account}.user"
    ipBankAddress = argv[argv.index("-i") + 1] if "-i" in argv else "127.0.0.1"
    bkPort = int(argv[argv.index("-p") + 1]) if "-p" in argv else 3000
    authFile = argv[argv.index("-s") + 1] if "-s" in argv else "bank.auth"

    # Verify if amount is in argv and if is a int
    if "-d" in argv and safe_execute("error",TypeError,float,argv[argv.index("-d")+1]) != "error":
        amount = float(argv[argv.index("-d") + 1])
    else:
        return 130
    
    if(amount <= 0): 
        print ("Invalid Amount") 
        return 130
        
    if not os.path.isfile(f"{current_working_directory}/src/MBec/usersFiles/{userFile}"):
        print(f"Error num 130")
        return 130


    m = json.dumps({"MessageType": "Deposit", "Amount":amount, "account":account})
    
    receivedMessage = json.loads(sendMessage(ipBankAddress,bkPort,m.encode('utf8')).decode('utf8'))
    
    if "account" in receivedMessage and "deposit" in receivedMessage:
        return receivedMessage
        
    else:
        print("Error")
        return 130


# mbec [-s <auth-file>] [-i <ip-bank-address>] [-p <bk-port>] [-u <user-file>] -a <account> -c <amount>
def createCardMode(argv:list[str]):

    # Terminal line inputs
    authFile = argv[argv.index("-s")+1] if "-s" in argv else "bank.auth"
    ipBankAddress = argv[argv.index("-i")+1] if "-i" in argv else "127.0.0.1"
    portStr = argv[argv.index("-p")+1] if "-p" in argv else 3000
    bkPort = int(portStr) if safe_execute("error",TypeError,int,portStr) != "error" else 3000
    account = argv[argv.index("-a")+1] if "-a" in argv else sys.exit(0)
    userFile = argv[argv.index("-u")+1] if "-u" in argv else f"{account}.user"

    # Verify if amount is in argv and if is a int
    if "-c" in argv and safe_execute("error",TypeError,float,argv[argv.index("-c")+1]) != "error":
        amount = float(argv[argv.index("-c")+1])
    else:
        return 130

    # Check if user file already exists
    if not os.path.isfile(f"{current_working_directory}/src/MBec/usersFiles/{userFile}"):
        return 130

    # Check if credit card initial amount is above 0
    if amount <= 0:
        return 130

    # Generate message
    newCardMessage = json.dumps({
        "MessageType": "CreateCard",
        "account": account,
        "amount": amount,
    }).encode('utf8')

    # Send receive message from Bank
    messageEncode = sendMessage(ipBankAddress,bkPort,newCardMessage)
    returnMessage = json.loads(messageEncode.decode('utf8'))

    # Check if Bank response is valid or Error 
    if "account" and "vcc_amount" and "vcc_file" in returnMessage:
        # Valid message
        return returnMessage
    else:
        # Error from Bank
        return 130


# mbec [-s <auth-file>] [-i <ip-bank-address>] [-p <bk-port>] [-u <user-file>] -a <account> -g
def getBalanceMode(argv:list[str]):
    
    # Verify if account is in argv
    if "-a" in argv:
        account = argv[argv.index("-a")+1]
    else: 
        return 130
    
    # it must be the same file produced by mbec when the account was created
    userFile = argv[argv.index("-u") + 1] if "-u" in argv else f"{account}.user"
    ipBankAddress = argv[argv.index("-i") + 1] if "-i" in argv else "127.0.0.1"
    bkPort = int(argv[argv.index("-p") + 1]) if "-p" in argv else 3000
    authFile = argv[argv.index("-s") + 1] if "-s" in argv else "bank.auth"
    
    if not os.path.isfile(f"{current_working_directory}/src/MBec/usersFiles/{userFile}"):
        return 130
        
    m = json.dumps({"MessageType": "Balance", "account":account})
    
    receivedMessage = json.loads(sendMessage(ipBankAddress,bkPort,m.encode('utf8')).decode('utf8'))
    
    if "account" in receivedMessage and "balance" in receivedMessage:
        return receivedMessage
    else:
        return 130



# mbec [-i <ip-store-address>] [-p <st-port>] [-v <virtual-credit-card-file>] -m <shopping-value>
def withdrawMode(argv:list[str]):

    # Terminal line inputs
    ipStoreAddress = argv[argv.index("-i")+1] if "-i" in argv else "127.0.0.1"
    portStr = argv[argv.index("-p")+1] if "-p" in argv else 5000
    stPort = int(portStr) if safe_execute("error",TypeError,int,portStr) != "error" else 3000

    # Verify the virtual credit card file
    if "-v" in argv:
        virtualCreditCardFile = argv[argv.index("-v")+1]
    else:
        return 130

    # 
    if "-m" in argv and safe_execute("error",TypeError,int,argv[argv.index("-m")+1]) != "error":
        shoppingValue = int(argv[argv.index("-m")+1])
    else:
        return 130

    # Check if the withdrawn amount is above 0
    if shoppingValue <= 0:
        return 130

    # Generate message
    withdrawCard = json.dumps({
        "MessageType": "WithdrawCard",
        "CreditCardFile": virtualCreditCardFile,
        "ShoppingValue": shoppingValue,
    }).encode('utf8')
    
    # Send receive message from Bank
    messageEncode = sendMessage(ipStoreAddress,stPort,withdrawCard)
    
    returnMessage = json.loads(messageEncode.decode('utf8'))
    


    return returnMessage
