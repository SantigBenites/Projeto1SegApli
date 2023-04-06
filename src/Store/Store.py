import json
import pickle
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
            #authFile
            (conn, addr) = receiveNewConnection(socket)
            
            receiveMsg,derived_key = receiveMessage(conn)
            
            withdrawCardMessage = pickle.loads(receiveMsg)
            
            if "MessageType" and "content" in withdrawCardMessage:
                if withdrawCardMessage["MessageType"] == "WithdrawCard":
                    
                    fileContent = pickle.loads(withdrawCardMessage["content"])
                    
                    if "ip" and "port" and "message" and"signature" not in fileContent:
                        #erro
                        return
                    #messagetoAuthenticate has to have a MessageType
                    messageToAuthenticate = pickle.loads({"message": fileContent["message"], "signature": fileContent["signature"]})
                    
                    data = sendMessageToBank(fileContent["ip"],fileContent["port"],messageToAuthenticate)
                    
                    message = json.loads(data.decode('utf8'))
                    
                    print(message)
                    sendMessage(conn,data,derived_key)
            
            
    
    
    except KeyboardInterrupt:
        sys.exit()
    
if __name__ == "__main__":
   main(sys.argv[1:])