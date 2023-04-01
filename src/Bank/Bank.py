import socket, sys, getopt, signal
from BankConnection import receiveConnection
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
        data = connection.recv(1024)
        if not data:
            break
        connection.sendall(data)

def exit(_signo, _stack_frame):
    sys.exit(0)

if __name__ == "__main__":
   main(sys.argv[1:])