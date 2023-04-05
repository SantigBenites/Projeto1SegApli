import socket, sys, getopt, signal, json, threading
from subprocess import *
from BankConnection import *
from BankModes import *
from BankStorage import *
from utils import *
from Cripto import *
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
    # Current Threads
    threads:list[threading.Thread] = []

    try:
        while loopBool:

            (conn,addr) = receiveNewConnection(socket)
            x = threading.Thread(target=new_threaded_client, args=(conn,))
            threads.append(x)
            x.start()
            
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
        sys.exit()


def new_threaded_client(conn):
    message,derived_key = receiveMessage(conn)
    message = json.loads(message.decode('utf8'))
    
    if "MessageType" in message:
        match message["MessageType"]:
            case "NewAccount":
                response = newAccountMode(message)
                sendMessage(conn,response,derived_key)
            case "Deposit":
                response = depositMode(message)
                sendMessage(conn, response,derived_key)
            case "Balance":
                response = getBalanceMode(message)
                sendMessage(conn, response,derived_key)
            case "CreateCard":
                response = createCardMode(message)
                sendMessage(conn,response,derived_key)
            case "WithdrawCard":
                response = withdrawMode(message)
                sendMessage(conn,response,derived_key)

                print(response)
    conn.close()

def exit(_signo, _stack_frame):
    sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])