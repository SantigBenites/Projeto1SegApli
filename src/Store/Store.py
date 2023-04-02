import json
import socket
import sys
from StoreConnection import *



def main(argv: list[str]):
    
    IPBANK = "127.0.0.1"
    PORT = 3000


    stPort = int(argv[argv.index("-p") + 1]) if "-p" in argv else 5000
    authFile = argv[argv.index("-s") + 1] if "-s" in argv else "bank.auth"

    socket = createSocket(port=stPort)
    
    
    try:
        while True:

            (conn, addr) = receiveNewConnection(socket)
            
            message = receiveMessage(conn)
            
            messagel = json.loads(message.decode('utf8'))
            
            if messagel["MessageType"] == "WithdrawCard":
                data = sendMessageToBank(IPBANK,PORT,message)
                
                message = json.loads(data.decode('utf8'))
                
                print(message)
                sendMessage(conn,data)
            
            
    
    
    except KeyboardInterrupt:
        sys.exit()
    
if __name__ == "__main__":
   main(sys.argv[1:])