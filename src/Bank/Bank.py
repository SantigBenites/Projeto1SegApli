import socket, sys, getopt, signal, json
from BankConnection import *
from BankModes import *
from BankStorage import *
from utils import *

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
    
    # Start Storage
    storage = BankStorageSingleton()

    try:
        while loopBool:

            (conn,addr) = receiveNewConnection(socket)
            message = receiveMessage(conn)
            message = json.loads(message.decode('utf8'))

            match message["MessageType"]:
                case "NewAccount":
                    response = newAccountMode(message)
                    sendMessage(conn,response)
                case "Deposit":
                    response = depositMode(message)
                    sendMessage(conn, response)
                case "Balance":
                    response = getBalanceMode(message)
                    sendMessage(conn, response)
                case "CreateCard":
                    response = createCardMode(message)
                    sendMessage(conn,response)
                case "WithdrawCard":
                    response = withdrawMode(message)
                    sendMessage(conn,response)

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