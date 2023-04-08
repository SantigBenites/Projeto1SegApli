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
    
    pathAuthFile =f"{current_working_directory}/src/Store/{authFile}"
    
    if  not os.path.isfile(pathAuthFile):
        return 130
    
    publicKeyBank = getPublicKeyFromCertFile(pathAuthFile)
    
    privateKey = getPrivateKey()
    publicKey = getPublicKey(privateKey)
    
    try:
        while True:
            #authFile verificar que exixt
            (conn, addr) = receiveNewConnection(socket)
            
            receiveMsg,derived_key = receiveMessage(conn)

            
            withdrawCardMessage = pickle.loads(receiveMsg)
            
            
            #print(withdrawCardMessage)
            
            if "MessageType" and "contentFile" and "ShoppingValue" and "IPClient" and "portClient" in withdrawCardMessage:
                if withdrawCardMessage["MessageType"] == "WithdrawCard":
                    
                    fileContent = withdrawCardMessage["contentFile"]
                    
                    #print(fileContent)
                    
                    if "ip" and "port" and "message" and"signature" not in fileContent:
                        #erro
                        return
                    
                    print(len(fileContent["message"]))
                    #messagetoAuthenticate has to have a MessageType
                    messageToAuthenticate = pickle.dumps({"message": pickle.dumps({"MessageType":"WithdrawCard", "content":  fileContent["message"],"ShoppingValue":withdrawCardMessage["ShoppingValue"],"IPClient":withdrawCardMessage["IPClient"], "portClient":withdrawCardMessage["portClient"]}), "signature": fileContent["signature"]})

                    data = sendMessageToBank(fileContent["ip"],fileContent["port"],messageToAuthenticate,publicKeyBank,privateKey,publicKey)
                    
                    messageSigned = pickle.loads(data)
                    
                    if not verifySignature(publicKeyBank,messageSigned["signature"],messageSigned["message"]):
                        sendMessage(conn,json.dumps({"Error": 130}.encode(),derived_key))
                        
                    message = json.loads(messageSigned["message"])
                    
                    if "vcc_file" and "vcc_amount_used" not in message:
                        sendMessage(conn,json.dumps({"Error": 130}).encode(),derived_key)
                    
                    print(message)
                    sendMessage(conn,messageSigned["message"],derived_key)
            
            
    
    
    except KeyboardInterrupt:
        sys.exit()
    
if __name__ == "__main__":
   main(sys.argv[1:])