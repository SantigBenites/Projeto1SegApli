import pickle
import secrets
import sys, socket, json, os
from utils import *
from Cripto import *
from MBecConnection import *

current_working_directory = os.getcwd()
lastUsedAccount = None

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
    
    # Generate message
    newAccountMessage = pickle.dumps({
        "MessageType": "NewAccount",
        "account": account,
        "balance": balance
    })
    
    #reads public Key
    publicKeyBank = getPublicKeyFromCertFile(pathAuthFile)

    # Send receive message from Bank
    messageEncode = sendMessage(ipBankAddress,bkPort,newAccountMessage,privateKey,publicKeyBank,account,publicKey)
    
    signedMessage = pickle.loads(messageEncode)
    
    if "message" and "signature" not in signedMessage:
        return 130
    
    returnMessage = json.loads(signedMessage["message"].decode('utf8'))
    
    if not verifySignature(publicKeyBank,signedMessage["signature"],signedMessage["message"]):
        return 130

    # Check if Bank response is valid or Error 
    if "account" in returnMessage and "initial_balance" in returnMessage:
        uploadPrivateKeyToFile(privateKey,pathUserFile)
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

    m = pickle.dumps({"MessageType": "Deposit", "Amount":amount, "account":account})
    
    publicKey = getPublicKey(privateKey)
    
    signedMessage = pickle.loads(sendMessage(ipBankAddress,bkPort,m,privateKey,publicKeyBank,account,publicKey))
    
    if "message" and "signature" not in signedMessage:
        return 130
    
    receivedMessage = json.loads(signedMessage["message"].decode('utf8'))
    
    if not verifySignature(publicKeyBank,signedMessage["signature"],signedMessage["message"]):
        return 130
    
    
    if "account" in receivedMessage and "deposit" in receivedMessage:
        lastUsedAccount=account
        return receivedMessage
        
    else:
        print("Error")
        return 130


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
        "amount": amount
    })


    publicKey = getPublicKey(privateKey)
    # Send receive message from Bank
    messageEncode = sendMessage(ipBankAddress,bkPort,newCardMessage,privateKey,publicKeyBank,account,publicKey)
    signedMessage = pickle.loads(messageEncode)

    if "message" and "signature" not in signedMessage:
        return 130
    
    returnMessage = json.loads(signedMessage["message"].decode('utf8'))

    if not verifySignature(publicKeyBank,signedMessage["signature"],signedMessage["message"]):
        return 130


    # Check if Bank response is valid or Error 
    if "account" and "vcc_amount" and "vcc_file" in returnMessage:
        # Valid message
        
        path = f"{current_working_directory}/src/MBec/creditCard/{returnMessage['vcc_file']}"
        
        #send rollback to server
        if os.path.isfile(path) and account != returnMessage["account"] and amount != returnMessage["vcc_amount"] :
            return 130
        
        
        
        messageEncripedPublicKeyBank = encryptDataWithPublicKey(publicKeyBank,signedMessage["message"])
        
        #encriptedWithMessageType = pickle.dumps({"MessageType":"WithdrawCard", "encrypted": messageEncripedPublicKeyBank})
        
        signature = signwithPrivateKey(privateKey,messageEncripedPublicKeyBank)
        contentFile = pickle.dumps({"ip": ipBankAddress, "port": bkPort, "message":messageEncripedPublicKeyBank, "signature": signature })
        
        
        print(len(messageEncripedPublicKeyBank))
        #print(messageEncripedPublicKeyBank)
        
        file = open(path,"wb")
        file.write(contentFile)
        file.close()
                
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
     
    m = pickle.dumps({"MessageType": "Balance", "account":account})
    
    publicKey = getPublicKey(privateKey)
    
    signedMessage = pickle.loads(sendMessage(ipBankAddress,bkPort,m,privateKey,publicKeyBank,account,publicKey))
    
    if "message" and "signature" not in signedMessage:
        return 130
    
    receivedMessage = json.loads(signedMessage["message"].decode('utf8'))
    
    if "account" in receivedMessage and "balance" in receivedMessage:
        lastUsedAccount=account
        return receivedMessage
    else:
        return 130



# mbec [-i <ip-store-address>] [-p <st-port>] [-v <virtual-credit-card-file>] -m <shopping-value>
def withdrawMode(argv:list[str]):

    # Terminal line inputs
    ipStoreAddress = argv[argv.index("-i")+1] if "-i" in argv else "127.0.0.1"
    portStr = argv[argv.index("-p")+1] if "-p" in argv else 5000
    stPort = int(portStr) if safe_execute("error",TypeError,int,portStr) != "error" else 5000

    # Verify the virtual credit card file
    if "-v" in argv:
        virtualCreditCardFile = argv[argv.index("-v")+1]
    else:
        #find file
        return 130
    

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
            print(argsAreValidIPv4(ipStoreAddress))
            print(argsAreValidPort(stPort))
            print(argsAreValidBalances(shoppingValue))
            print(argsAreValidFileNames(virtualCreditCardFile))
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
        

    
    #print("pickleloads:")
    print(len(p["message"]))
    # Generate message
    withdrawCard = pickle.dumps({
        "MessageType": "WithdrawCard",
        "contentFile": p,
        "ShoppingValue": shoppingValue
    })
    
    
    # Send receive message to Store
    messageEncode = sendMessageToStore(ipStoreAddress,stPort,withdrawCard)
    

    returnMessage = json.loads(messageEncode.decode('utf8'))



    return returnMessage
