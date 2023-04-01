import socket, sys, getopt, signal, json
from BankConnection import receiveConnection, receiveMessage, sendMessage
from BankModes import *
from utils import safe_execute

loopBool = True

def main(argv:list[str]):
    

    # Signals
    signal.signal(signal.SIGINT, exit)

    # Processing Arguments
    portStr = argv[argv.index("-p")+1] if "-p" in argv else 3000
    portNumber = int(portStr) if safe_execute(0,TypeError,int,portStr) != 0 else 3000
    authFile = argv[argv.index("-s")+1] if "-s" in argv else "bank.auth"
    
    connection,address = receiveConnection(port=portNumber)
    while loopBool:
        message = receiveMessage(connection)
        if not message:
            break
        
        message = json.loads(message.decode('utf8'))

        if message["MessageType"] == "NewAccount":
            response = newAccountMode(message)
            sendMessage(connection,response)


def exit(_signo, _stack_frame):
    sys.exit(0)

if __name__ == "__main__":
   main(sys.argv[1:])