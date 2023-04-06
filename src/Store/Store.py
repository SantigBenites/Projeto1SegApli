import json
import os
import pickle
import socket
import sys
from StoreConnection import *


current_working_directory = os.getcwd()
def main(argv: list[str]):
    
    IPBANK = "127.0.0.1"
    PORT = 3000


    stPort = int(argv[argv.index("-p") + 1]) if "-p" in argv else 5000
    authFile = argv[argv.index("-s") + 1] if "-s" in argv else "bank.auth"

    socket = createSocket(port=stPort)
    
    pathAuthFile =f"{current_working_directory}/src/MBec/{authFile}"
    
    if  not os.path.isfile(pathAuthFile):
        return 130
    
    publicKeyBank = getPublicKeyFromCertFile(pathAuthFile)
    
    try:
        while True:
            #authFile
            (conn, addr) = receiveNewConnection(socket)
            
            receiveMsg,derived_key = receiveMessage(conn)

            
            withdrawCardMessage = pickle.loads(receiveMsg)
            print(withdrawCardMessage)
            
            if "MessageType" and "contentFile" in withdrawCardMessage:
                if withdrawCardMessage["MessageType"] == "WithdrawCard":
                    
                    fileContent = withdrawCardMessage["contentFile"]
                    
                    print(fileContent)
                    
                    if "ip" and "port" and "message" and"signature" not in fileContent:
                        #erro
                        return
                    #messagetoAuthenticate has to have a MessageType
                    messageToAuthenticate = pickle.dumps({"message": json.dumps({"MessageType":"WithdrawCard", "content":  fileContent["message"]}).encode(), "signature": fileContent["signature"]})
                    
                    data = sendMessageToBank(fileContent["ip"],fileContent["port"],messageToAuthenticate,publicKeyBank)
                    
                    message = json.loads(data.decode('utf8'))
                    
                    print(message)
                    sendMessage(conn,data,derived_key)
            
            
    
    
    except KeyboardInterrupt:
        sys.exit()
    
if __name__ == "__main__":
   main(sys.argv[1:])