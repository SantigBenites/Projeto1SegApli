import socket, sys, getopt, signal
from utils import safe_execute


def main(argv:list[str]):

    if "-n" in argv:
        messageDict = newAccountMode()
    elif "-d" in argv:
        messageDict = depositMode()
    elif "-c" in argv:
        messageDict = createCardMode()
    elif "g" in argv:
        messageDict = getBalanceMode()
    elif "-m"in argv:
        messageDict = withrawMode()
    else:
        sys.exit(1)
    


    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b"Hello, world")
        data = s.recv(1024)
    
    print(f"Received {data!r}")


if __name__ == "__main__":
   main(sys.argv[1:])