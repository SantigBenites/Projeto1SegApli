import pickle
import secrets
import sys, socket, json, os
from time import sleep
from utils import *
from Cripto import *
from MBecConnection import *
from MBecServerMode import *

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
    
    # Verify if balance is in argv
    if "-n" in argv:
        balance = argv[argv.index("-n")+1]
    else:
        return 130
    
    # All Validation for all inputs
    if  not (
        argsAreValidAccountNames(account) and
        argsAreValidFileNames(authFile) and
        argsAreValidIPv4(ipBankAddress) and 
        argsAreValidPort(bkPort) and 
        argsAreValidFileNames(userFile) and 
        argsAreValidBalances(balance)):
            return 130
    
    # Verify if balance is float
    if safe_execute("error",TypeError,float,argv[argv.index("-n")+1]) != "error":
        balance = float(argv[argv.index("-n")+1])
    else:
        return 130

    # Check if initial balance is above 15
    if balance < 15:
        return 130
    
    #checks the existence of authFile
    pathAuthFile =f"{current_working_directory}/src/MBec/{authFile}"
    
    if  not os.path.isfile(pathAuthFile):
        return 130
    
    if os.path.isfile(f"{current_working_directory}/src/MBec/usersFiles/{userFile}"):
        return 130
    
    pathUserFile =f"{current_working_directory}/src/MBec/usersFiles/{userFile}"
    
    privateKey = getPrivateKey()
    
    publicKey = getPublicKey(privateKey)
    
    #reads public Key
    publicKeyBank = getPublicKeyFromCertFile(pathAuthFile)
    
    # Generate message
    newAccountMessage = pickle.dumps({
        "MessageType": "NewAccount",
        "account": account,
        "balance": balance,
        "timeStamp": getTimeStamp()
    })
    

    # Send receive message from Bank
    messageEncode = sendMessage(ipBankAddress,bkPort,newAccountMessage,privateKey,publicKeyBank,account,publicKey)
    
    if messageEncode == None:
        print("protocol_error")
        return 63
    
    
    hashedMessage = pickle.loads(messageEncode)
    
    if "messageHashed" not in hashedMessage or "hash" not in hashedMessage:
        return 130
    
    
    if not verifyHash(hashedMessage):
    #if True:

        rollBackmessage = pickle.dumps({
            "MessageType": "RollBack",
            "OriginalMessageType": "NewAccount",
            "account": account,
            "balance": balance,
            "timeStamp": getTimeStamp()
        })
        sendRollBackMessage(ipBankAddress,bkPort,rollBackmessage,privateKey,publicKeyBank,account,publicKey)

        return 130
    
    signedMessage = pickle.loads(hashedMessage["messageHashed"])
    
    if "message" not in signedMessage or  "signature" not in signedMessage:
        return 130
    
    returnMessage = json.loads(signedMessage["message"].decode('utf8'))
    
    if not verifySignature(publicKeyBank,signedMessage["signature"],signedMessage["message"]):
        return 130

    # Check if Bank response is valid or Error 
    if "account" not in returnMessage or "initial_balance" not in returnMessage:
        return 130
    
    global lastUsedAccount
    lastUsedAccount = account
    uploadPrivateKeyToFile(privateKey,pathUserFile)
    return returnMessage





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
    if "-d" in argv:
        amount = argv[argv.index("-d") + 1]
    else:
        return 130
    
    # All Validation for all inputs
    if  not (
        argsAreValidAccountNames(account) and
        argsAreValidFileNames(userFile) and 
        argsAreValidIPv4(ipBankAddress) and 
        argsAreValidPort(bkPort) and 
        argsAreValidFileNames(authFile) and
        argsAreValidBalances(amount)):

            print(amount)

            return 130
    

    # Verify if amount is float
    if safe_execute("error",TypeError,float,argv[argv.index("-d")+1]) != "error":
        amount = float(argv[argv.index("-d") + 1])
    else:
        return 130

    
    if(amount <= 0): 
        print ("Invalid Amount") 
        return 130
        
    filePath = f"{current_working_directory}/src/MBec/usersFiles/{userFile}"
    if not os.path.isfile(filePath):
        print(f"Error num 130")
        return 130
    
    #checks the existence of authFile
    pathAuthFile =f"{current_working_directory}/src/MBec/{authFile}"
    
    if  not os.path.isfile(pathAuthFile):
        return 130
    
    #reads public Key
    publicKeyBank = getPublicKeyFromCertFile(pathAuthFile)
    
    
    privateKey = readPrivateKeyFromFile(filePath)

    m = pickle.dumps({"MessageType": "Deposit",
                      "Amount":amount, 
                      "account":account,
                      "timeStamp": getTimeStamp()
                    })
    
    publicKey = getPublicKey(privateKey)
    
    messageEncode = sendMessage(ipBankAddress,bkPort,m,privateKey,publicKeyBank,account,publicKey)
    
    if messageEncode == None:
        print("protocol_error")
        return 63
    
    hashedMessage = pickle.loads(messageEncode)
    
    if "messageHashed" not in hashedMessage or "hash" not in hashedMessage:
            return 130
    
    
    if not verifyHash(hashedMessage):
    #if True:
        rollBackmessage = pickle.dumps({
            "MessageType": "RollBack",
            "OriginalMessageType": "Deposit",
            "Amount": amount,
            "account": account,
            "timeStamp": getTimeStamp()
        })
        sendRollBackMessage(ipBankAddress,bkPort,rollBackmessage,privateKey,publicKeyBank,account,publicKey)

        return 130
    
    signedMessage = pickle.loads(hashedMessage["messageHashed"])
    
    if "message" not in signedMessage or "signature" not in signedMessage:
        return 130
    
    receivedMessage = json.loads(signedMessage["message"].decode('utf8'))
    
    if not verifySignature(publicKeyBank,signedMessage["signature"],signedMessage["message"]):
        return 130
    
    
    if "account" not in receivedMessage or "deposit" not in  receivedMessage:
        return 130
    
    global lastUsedAccount
    lastUsedAccount = account
    return receivedMessage



# mbec [-s <auth-file>] [-i <ip-bank-address>] [-p <bk-port>] [-u <user-file>] -a <account> -c <amount>
def createCardMode(argv:list[str]):

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

    # Verify if amount is in argv and if is a int
    if "-c" in argv:
        amount = argv[argv.index("-c")+1]
    else:
        return 130
    
    # All Validation for all inputs
    if  not (
        argsAreValidAccountNames(account) and
        argsAreValidFileNames(authFile) and
        argsAreValidIPv4(ipBankAddress) and 
        argsAreValidPort(bkPort) and 
        argsAreValidFileNames(userFile) and 
        argsAreValidBalances(amount)):
            return 130
    
    # Verify if amount is float
    if safe_execute("error",TypeError,float,argv[argv.index("-c")+1]) != "error":
        amount = float(argv[argv.index("-c") + 1])
    else:
        return 130

    # Check if user file already exists
    filePath = f"{current_working_directory}/src/MBec/usersFiles/{userFile}"
    if not os.path.isfile(filePath):
        print(f"Error num 130")
        return 130
    
    #checks the existence of authFile
    pathAuthFile =f"{current_working_directory}/src/MBec/{authFile}"
    
    if  not os.path.isfile(pathAuthFile):
        return 130
    
    #reads public Key
    publicKeyBank = getPublicKeyFromCertFile(pathAuthFile)
    
    privateKey = readPrivateKeyFromFile(filePath)

    # Check if credit card initial amount is above 0
    if amount <= 0:
        return 130
    
    # Generate message
    newCardMessage = pickle.dumps({
        "MessageType": "CreateCard",
        "account": account,
        "amount": amount,
        "timeStamp": getTimeStamp()
    })


    publicKey = getPublicKey(privateKey)
    # Send receive message from Bank
    messageEncode = sendMessage(ipBankAddress,bkPort,newCardMessage,privateKey,publicKeyBank,account,publicKey)
    
    if messageEncode == None:
        print("protocol_error")
        return 63
    
    
    hashedMessage = pickle.loads(messageEncode)
    
    if "messageHashed" not in hashedMessage or "hash" not in hashedMessage:
            return 130
    
    
    if not verifyHash(hashedMessage):
    #if True:
        rollBackmessage = pickle.dumps({
            "MessageType": "RollBack",
            "OriginalMessageType": "CreateCard",
            "account": account,
            "amount": amount,
            "timeStamp": getTimeStamp()
        })
        sendRollBackMessage(ipBankAddress,bkPort,rollBackmessage,privateKey,publicKeyBank,account,publicKey)

        return 130
    
    signedMessage = pickle.loads(hashedMessage["messageHashed"])


    if "message" not in signedMessage or "signature" not in signedMessage:
        return 130
    
    returnMessage = json.loads(signedMessage["message"].decode('utf8'))

    if not verifySignature(publicKeyBank,signedMessage["signature"],signedMessage["message"]):
        return 130


    # Check if Bank response is valid or Error 
    if "account" not in returnMessage or "vcc_amount" not in returnMessage or "vcc_file" not  in returnMessage:
        return 130
       
        
    path = f"{current_working_directory}/src/MBec/creditCard/{returnMessage['vcc_file']}"
    
    #send rollback to server
    if os.path.isfile(path):
    #if True :
        # Implement rollback
        # Generate message
        rollBackmessage = pickle.dumps({
            "MessageType": "RollBack",
            "OriginalMessageType": "CreateCard",
            "account": account,
            "amount": amount,
            "timeStamp": getTimeStamp()
        })
        sendRollBackMessage(ipBankAddress,bkPort,rollBackmessage,privateKey,publicKeyBank,account,publicKey)

        return 130 
    
    if account != returnMessage["account"] and amount != returnMessage["vcc_amount"] :

        return 130
    
    messageEncripedPublicKeyBank = encryptDataWithPublicKey(publicKeyBank,signedMessage["message"])
        
    signature = signwithPrivateKey(privateKey,messageEncripedPublicKeyBank)
    contentFile = pickle.dumps({"ip": ipBankAddress, "port": bkPort, "message":messageEncripedPublicKeyBank, "signature": signature })

    file = open(path,"wb")
    file.write(contentFile)
    file.close()
    
    global lastUsedAccount
    lastUsedAccount = account
    return returnMessage



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
    
    
    filePath = f"{current_working_directory}/src/MBec/usersFiles/{userFile}"
    if not os.path.isfile(filePath):
        return 130
    
    #checks the existence of authFile
    pathAuthFile =f"{current_working_directory}/src/MBec/{authFile}"
    if  not os.path.isfile(pathAuthFile):
        return 130
    
    #reads public Key
    publicKeyBank = getPublicKeyFromCertFile(pathAuthFile)

    privateKey = readPrivateKeyFromFile(filePath)
    
    # All Validation for all inputs
    if  not (
        argsAreValidAccountNames(account) and
        argsAreValidFileNames(userFile) and 
        argsAreValidIPv4(ipBankAddress) and 
        argsAreValidPort(bkPort) and 
        argsAreValidFileNames(authFile)):
            return 130
     
    m = pickle.dumps({"MessageType": "Balance",
                      "account":account,
                      "timeStamp": getTimeStamp()})
    
    publicKey = getPublicKey(privateKey)
    
    messageEncode = sendMessage(ipBankAddress,bkPort,m,privateKey,publicKeyBank,account,publicKey)
    
    if messageEncode == None:
        print("protocol_error")
        return 63
    
    hashedMessage = pickle.loads(messageEncode)
    
    if "messageHashed" not in hashedMessage or "hash" not in hashedMessage:
            return 130
    
    
    if not verifyHash(hashedMessage):
        return 130
    
    signedMessage = pickle.loads(hashedMessage["messageHashed"])

    
    if "message" not in signedMessage or "signature" not in signedMessage:
        return 130
    
    receivedMessage = json.loads(signedMessage["message"].decode('utf8'))
    
    if "account"  not in receivedMessage or "balance" not in receivedMessage:
        return 130
    
    global lastUsedAccount
    lastUsedAccount = account
    return receivedMessage




# mbec [-i <ip-store-address>] [-p <st-port>] [-v <virtual-credit-card-file>] -m <shopping-value>
def withdrawMode(argv:list[str]):

    # Terminal line inputs
    ipStoreAddress = argv[argv.index("-i")+1] if "-i" in argv else "127.0.0.1"
    portStr = argv[argv.index("-p")+1] if "-p" in argv else 5000
    stPort = int(portStr) if safe_execute("error",TypeError,int,portStr) != "error" else 5000

    # Verify the virtual credit card file
    global lastUsedAccount
    if "-v" in argv:
        virtualCreditCardFile = argv[argv.index("-v")+1]
    else:
        files = os.listdir(f"{current_working_directory}/src/MBec/creditCard")
        if lastUsedAccount != None:
            # We have the last used account
            valid_withUsedAccount = [x for x in files if re.search(f"{lastUsedAccount}_\d\.card$",x)]
            maxValue = max([int((re.search("_\d", cardNumber)[0])[1]) for cardNumber in valid_withUsedAccount])
            virtualCreditCardFile = f"{lastUsedAccount}_{maxValue}.card"
        else:
            # We dont have the last used account
            valid_withAnyAccount = [x for x in files if re.search("^.+_\d\.card$",x)]
            maxValue = max([int((re.search("_\d", cardNumber)[0])[1]) for cardNumber in valid_withAnyAccount])
            bestCards = [x for x in files if re.search(f"^.+_{maxValue}\.card$",x)]
            virtualCreditCardFile = bestCards[0]
    
    print(f"using card{virtualCreditCardFile}")
    # 
    if "-m" in argv:
        shoppingValue = argv[argv.index("-m")+1]
    else:
        return 130
    # All Validation for all inputs
    if  not (
        argsAreValidIPv4(ipStoreAddress) and 
        argsAreValidPort(stPort) and 
        argsAreValidBalances(shoppingValue) and
        argsAreValidFileNames(virtualCreditCardFile)):
            return 130
        
    # Verify if shoppingValue is float
    if safe_execute("error",TypeError,float,argv[argv.index("-m")+1]) != "error":
        shoppingValue = float(argv[argv.index("-m") + 1])
    else:
        return 130

    # Check if the withdrawn amount is above 0
    if shoppingValue <= 0:
        return 130

    #if -v is not given
    
    filePath = f"{current_working_directory}/src/MBec/creditCard/{virtualCreditCardFile}"
    
    if not os.path.isfile(filePath):
        return 130
    

    with open(filePath, "rb") as file:
        p = pickle.load(file)
        file.close()

    #recebe ligação do banco
    socket, ip, port = createSocket()
    withdrawCard = pickle.dumps({
        "MessageType": "WithdrawCard",
        "contentFile": p,
        "ShoppingValue": shoppingValue,
        "IPClient": ip ,
        "portClient":port,
        "timeStamp": getTimeStamp()
    })
    
    
    # Send receive message to Store
    messageEncode = sendMessageToStore(ipStoreAddress,stPort,withdrawCard,socket)
    
    if messageEncode == None:
        print("protocol_error")
        return 63
    
    hashedMessage = pickle.loads(messageEncode)
    
    if "messageHashed" not in hashedMessage or "hash" not in hashedMessage:
            return 130
    
    
    if not verifyHash(hashedMessage):
    #if True:
        rollBackmessage = pickle.dumps({
            "MessageType": "RollBack",
            "OriginalMessageType": "WithdrawCard",
            "contentFile": p,
            "ShoppingValue": shoppingValue,
            "timeStamp": getTimeStamp()
        })
        sendRollBackToStore(ipStoreAddress,stPort,rollBackmessage)

        return 130 
    
    #Ok
    returnMessage = json.loads(hashedMessage["messageHashed"])

    if "Error" in returnMessage:
        print("protocol_error")
        return 63

    return returnMessage
