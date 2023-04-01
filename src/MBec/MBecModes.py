import json, sys

def newAccountMode():
    return (destIP,destPort,messageJSON)


#mbec [-s <auth-file>] [-i <ip-bank-address>] [-p <bk-port>] [-u <user-file>] -a <account> -d <amount>
def depositMode(argv:"list[str]"):
    


    account = argv[argv.index("-a")+1] if argv.contains("-a") else exit(1)
    # it must be the same file produced by mbec when the account was created
    userFile = argv[argv.index("-u") + 1] if argv.contains("-u") else f"{account}.user"
    ipBankAddress = argv[argv.index("-i") + 1] if argv.contains("-i") else "127.0.0.1"
    bkPort = int(argv[argv.index("-p") + 1]) if argv.contains("-p") else 3000
    authFile = argv[argv.index("-s") + 1] if argv.contains("-s") else "bank.auth"
    amount = int(argv[argv.index("-d") + 1]) if argv.contains("-d") else exit(1)
    
    if(amount <= 0): 
        print ("Invalid Amount") 
        exit (1)

    m = json.dumps()
    return(ipBankAddress, bkPort, )



def createCardMode():
    return



def getBalanceMode():
    return



def withrawMode():
    return
