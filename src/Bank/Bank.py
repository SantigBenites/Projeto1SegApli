import socket, sys, getopt, signal, json
from BankConnection import *
from BankModes import *
from BankStorage import *
from utils import safe_execute

loopBool = True

def main(argv:list[str]):
    

    # Signals
    #signal.signal(signal.SIGINT, exit)

    # Processing Arguments
    portStr = argv[argv.index("-p")+1] if "-p" in argv else 3000
    portNumber = int(portStr) if safe_execute(0,TypeError,int,portStr) != 0 else 3000
    authFile = argv[argv.index("-s")+1] if "-s" in argv else "bank.auth"
    socket = createSocket(port=portNumber)
    
    # Start Storage
    storage = BankStorageSingleton()

    try:
        while loopBool:

            (conn,addr) = receiveNewConnection(socket)
            message = receiveMessage(conn)
            message = json.loads(message.decode('utf8'))

            if message["MessageType"] == "NewAccount":
                response = newAccountMode(message)
                sendMessage(conn,response)


            print(response)
            conn.close()
    except KeyboardInterrupt:
        print("Ended Properly")
        print(f"Storage: \n {storage.users}")
        conn.close()
        sys.exit()


def exit(_signo, _stack_frame):
    sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])