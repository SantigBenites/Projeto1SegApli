import pickle
import socket, sys, getopt, signal, json, threading, logging
from subprocess import *
from BankConnection import *
from BankModes import *
from BankStorage import *
from utils import *
from Cripto import *
from RollBack import *
#from _thread import *

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
    # Start sys out lock
    lock = threading.Lock()
    # Current Threads
    threads:list[threading.Thread] = []

    try:
        while loopBool:
            
            #nao podes fazer verificação da assinatura AQUI!!!
            #nao tem chave plica para comparar


            (conn,addr,account,PublicKeyClient) = receiveNewConnection(socket,privateKey)
            x = threading.Thread(target=new_threaded_client, args=(conn,lock,privateKey,account,PublicKeyClient))
            threads.append(x)
            x.start()
            x.join()
            
    except KeyboardInterrupt:
        # Ending properly

        # Printing current storage
        print("Ended Properly")
        print(f"Storage: \n {storage.users}")
        
        # Removing userFiles automatically, to remove in final version
        call(["python", "src/clearUserFiles.py"])

        # Joining threads
        for thr in threads:
            thr.join()

        # 
        if 'conn' in locals():
            conn.close()

        # Close socket
        socket.close()

        sys.exit()

def error_response(privateKey, conn, derived_key):
    response  = json.dumps({"Error":130}).encode('utf8')
    responseSigned = signedMessage(response,privateKey)
    hashedMessage = hashMessage(responseSigned)
    sendMessage(conn,hashedMessage,derived_key)
    print(response)
    sys.stdout.flush()
    conn.close()


def new_threaded_client(conn,lock,privateKey,account,PublicKeyClient):
    message,derived_key = receiveMessage(conn,PublicKeyClient,privateKey)
    
    hashedMessage = pickle.loads(message)
    
    if "messageHashed" not in hashedMessage or "hash" not in hashedMessage:
        error_response(privateKey, conn, derived_key)
        return
    
    if not verifyHash(hashedMessage):
        error_response(privateKey, conn, derived_key)
        return
    
    Signedmessage = pickle.loads(hashedMessage["messageHashed"])
    if "message" not in Signedmessage or "signature" not in Signedmessage:
        error_response(privateKey, conn, derived_key)
        return
    message = pickle.loads(Signedmessage["message"])
    if "MessageType" not  in message:
        error_response(privateKey, conn, derived_key)
        return
    
    print(message)

    if "account" in message:
        if message["account"] != account:
            error_response(privateKey, conn, derived_key)
            return
        else:
            match message["MessageType"]:
                case "NewAccount":
                    response = newAccountMode(Signedmessage,message,PublicKeyClient)
                    responseSigned = signedMessage(response,privateKey)
                    hashedMessage = hashMessage(responseSigned)
                    sendMessage(conn,hashedMessage,derived_key)
                case "Deposit":
                    response = depositMode(Signedmessage,message)
                    responseSigned = signedMessage(response,privateKey)
                    hashedMessage = hashMessage(responseSigned)
                    sendMessage(conn, hashedMessage,derived_key)
                case "Balance":
                    response = getBalanceMode(Signedmessage,message)
                    responseSigned = signedMessage(response,privateKey)
                    hashedMessage = hashMessage(responseSigned)
                    sendMessage(conn, hashedMessage,derived_key)
                case "CreateCard":
                    response = createCardMode(Signedmessage,message)
                    responseSigned = signedMessage(response,privateKey)
                    hashedMessage = hashMessage(responseSigned)
                    sendMessage(conn,hashedMessage,derived_key)
                case "RollBack":
                    RollBackEntry(Signedmessage,message)
                    return
    elif message["MessageType"] == "WithdrawCard":
        response = withdrawMode(Signedmessage,message,privateKey,PublicKeyClient)
        responseSigned = signedMessage(response,privateKey)
        hashedMessage = hashMessage(responseSigned)
        sendMessage(conn,hashedMessage,derived_key)
    else:
        error_response(privateKey,conn,derived_key)
        return

    with lock:
        print(response)
        sys.stdout.flush()
    conn.close()

def exit(_signo, _stack_frame):
    sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])