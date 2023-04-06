import pickle
import socket, sys, getopt, signal, json
from BankConnection import *
from BankModes import *
from BankStorage import *
from utils import *
from Cripto import *

loopBool = True

def main(argv:list[str]):
    

    # Signals
    #signal.signal(signal.SIGINT, exit)
    argv = stringToArgs("".join(argv))

    # Processing Arguments
    portStr = argv[argv.index("-p")+1] if "-p" in argv else 3000
    portNumber = int(portStr) if safe_execute("error",TypeError,int,portStr) != "error" else 3000
    authFile = argv[argv.index("-s")+1] if "-s" in argv else "bank.auth"
    socket = createSocket(port=portNumber)
    
    current_working_directory = os.getcwd()
    
    if os.path.isfile(f"{current_working_directory}/src/Bank/auth/{authFile}"):
        sys.exit()
        
    
    
    privateKey = getPrivateKey()
    cert = generateSelfSignedCert(privateKey, f"{current_working_directory}/src/Bank/auth/{authFile}")

    # Start Storage
    storage = BankStorageSingleton()

    try:
        while loopBool:
            
            #nao podes fazer verificação da assinatura AQUI!!!
            #nao tem chave plica para comparar

            (conn,addr) = receiveNewConnection(socket,privateKey)
            message,derived_key = receiveMessage(conn)
            Signedmessage = pickle.loads(message)
            
            print(message)
            if "message" and "signature" in Signedmessage:
                message = json.loads(Signedmessage["message"].decode())
                print(message)
                if "MessageType" in message:
                    match message["MessageType"]:
                        case "NewAccount":
                            response = newAccountMode(Signedmessage,message)
                            responseSigned = signedMessage(response,privateKey)
                            sendMessage(conn,responseSigned,derived_key)
                        case "Deposit":
                            response = depositMode(Signedmessage,message)
                            responseSigned = signedMessage(response,privateKey)
                            sendMessage(conn, responseSigned,derived_key)
                        case "Balance":
                            response = getBalanceMode(Signedmessage,message)
                            responseSigned = signedMessage(response,privateKey)
                            sendMessage(conn, responseSigned,derived_key)
                        case "CreateCard":
                            response = createCardMode(Signedmessage,message)
                            responseSigned = signedMessage(response,privateKey)
                            sendMessage(conn,responseSigned,derived_key)
                        case "WithdrawCard":
                            response = withdrawMode(Signedmessage,message)
                            responseSigned = signedMessage(response,privateKey)
                            sendMessage(conn,responseSigned,derived_key)

                    print(response)
            conn.close()
    except KeyboardInterrupt:
        print("Ended Properly")
        print(f"Storage: \n {storage.users}")
        if 'conn' in locals():
            conn.close()
        sys.exit()


def exit(_signo, _stack_frame):
    sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])