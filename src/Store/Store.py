import json
import os
import pickle
import socket
import sys
from StoreConnection import *
from utils import *


current_working_directory = os.getcwd()
def main(argv: list[str]):
    
    argv = stringToArgs("".join(argv))
    if argv == None or argv == 130:
        sys.exit(125)

    portStr = argv[argv.index("-p")+1] if "-p" in argv else 5000
    stPort = int(portStr) if safe_execute("error",TypeError,int,portStr) != "error" else 5000
    authFile = argv[argv.index("-s") + 1] if "-s" in argv else "bank.auth"

    if not(
        argsAreValidPort(stPort) and
        argsAreValidFileNames(authFile)):
            sys.exit(125)

    socket = createSocket(port=stPort)
    
    pathAuthFile =f"{current_working_directory}/src/Store/{authFile}"
    
    if  not os.path.isfile(pathAuthFile):
        return sys.exit(135)
    
    publicKeyBank = getPublicKeyFromCertFile(pathAuthFile)
    
    privateKey = getPrivateKey()
    publicKey = getPublicKey(privateKey)
    
    try:
        while True:
            (conn, addr) = receiveNewConnection(socket)
            
            result = receiveMessage(conn)
            if result == None:
                conn.close()
                continue
            receiveMsg,derived_key = result
            hashedMessage = pickle.loads(receiveMsg)
    
            if "messageHashed" not in hashedMessage or "hash" not in hashedMessage:
                sendMessage(conn,json.dumps({"Error": 130, "timeStamp": getTimeStamp()}).encode(),derived_key)
                conn.close()
                continue
            
            
            if not verifyHash(hashedMessage):
                sendMessage(conn,json.dumps({"Error": 130, "timeStamp": getTimeStamp()}).encode(),derived_key)
                conn.close()
                continue
            

            withdrawCardMessage = pickle.loads(hashedMessage["messageHashed"])

            if "MessageType" not in  withdrawCardMessage:
                sendMessage(conn,json.dumps({"Error": 130,"timeStamp": getTimeStamp()}).encode(),derived_key)
                conn.close()
                continue
            
            
            
            match withdrawCardMessage["MessageType"]:
                case "WithdrawCard":
                    
                    if "contentFile" not in  withdrawCardMessage or "ShoppingValue" not in  withdrawCardMessage or "IPClient" not in  withdrawCardMessage or "portClient" not in withdrawCardMessage:
                        sendMessage(conn,json.dumps({"Error": 130,"timeStamp": getTimeStamp()}).encode(),derived_key)
                        conn.close()
                        continue
                        
                    fileContent = withdrawCardMessage["contentFile"]
                    if "ip" not in fileContent or  "port" not in fileContent or "message" not in fileContent or "signature" not in fileContent:
                        sendMessage(conn,json.dumps({"Error": 130,"timeStamp": getTimeStamp()}).encode(),derived_key)
                        conn.close()
                        continue

                    msgTime = pickle.dumps({"MessageType": "WithdrawCard", "messageClient": hashedMessage["messageHashed"], "timeStamp": getTimeStamp()})
                    
                    signature = signwithPrivateKey(privateKey, msgTime)
                    
                    
                    msg =  pickle.dumps({"message": msgTime,"signature": signature})
                    
                    data = sendMessageToBank(fileContent["ip"],fileContent["port"],msg,publicKeyBank,privateKey,publicKey)
                    
                    if data == None:
                        print("protocol_error\n")
                        sys.stdout.flush()
                        sendMessage(conn,json.dumps({"Error": 63,"timeStamp": getTimeStamp()}).encode(),derived_key)
                        conn.close()
                        continue
                    
                    
                    hashedMessage = pickle.loads(data)
                    
                    if "messageHashed" not in hashedMessage or "hash" not in hashedMessage:
                        sendMessage(conn,json.dumps({"Error": 130,"timeStamp": getTimeStamp()}).encode(),derived_key)
                        conn.close()
                        continue
                    
                    if not verifyHash(hashedMessage):
                        sendMessage(conn,json.dumps({"Error": 130,"timeStamp": getTimeStamp()}).encode(),derived_key)
                        conn.close()
                        continue
                    
                    
                    messageSigned = pickle.loads(hashedMessage["messageHashed"])
                    
                    if not verifySignature(publicKeyBank,messageSigned["signature"],messageSigned["message"]):
                        sendMessage(conn,json.dumps({"Error": 130,"timeStamp": getTimeStamp()}.encode(),derived_key))
                        conn.close()
                        continue
                        
                    message = json.loads(messageSigned["message"])
                    
                    if "vcc_file" not in message or "vcc_amount_used" not in message or "timeStamp" not in message :
                        print(message)
                        sys.stdout.flush()
                        sendMessage(conn,json.dumps({"Error": 130,"timeStamp": getTimeStamp()}).encode(),derived_key)
                        conn.close()
                        continue
                    
                    if not verifyTimeStampValidity(message["timeStamp"]):
                        print(message)
                        sys.stdout.flush()
                        sendMessage(conn,json.dumps({"Error": 130,"timeStamp": getTimeStamp()}).encode(),derived_key)
                        conn.close()
                        continue
                    
                    print(message)
                    sys.stdout.flush()
                    
                    msg = json.dumps({"vcc_file": message["vcc_file"],
                                    "vcc_amount_used": message["vcc_amount_used"],
                                    "bankStamp": message["timeStamp"],
                                    "storeStamp": getTimeStamp()}).encode()

                    message = sendMessage(conn,msg,derived_key)
                    if message == None:
                        print("protocol_error\n")
                        sys.stdout.flush()

                        message = pickle.dumps({"MessageType": "RollBack",
                                            "OriginalMessageType": "WithdrawCard",
                                            "contentFile": withdrawCardMessage["contentFile"],
                                            "ShoppingValue": withdrawCardMessage["ShoppingValue"],
                                            "timeStamp": getTimeStamp()})
                        
                        signature = signwithPrivateKey(privateKey, message)
                    
                        msg =  pickle.dumps({"message": message, "signature": signature})
                        
                        # Rollback to Bank
                        sendRollBackToBank(fileContent["ip"],fileContent["port"],msg,publicKeyBank,privateKey,publicKey)
                       
                        conn.close()
                        continue
                    conn.close()
                    
                case "RollBack":
                    if "contentFile" not in  withdrawCardMessage or "ShoppingValue" not in  withdrawCardMessage or "OriginalMessageType" not in  withdrawCardMessage:
                        sendMessage(conn,json.dumps({"Error": 130}).encode(),derived_key)
                        conn.close()
                        continue
                    

                    signature = signwithPrivateKey(privateKey, hashedMessage["messageHashed"])
                    
                    msg =  pickle.dumps({"message": hashedMessage["messageHashed"], "signature": signature})
                    
                    sendRollBackToBank(fileContent["ip"],fileContent["port"],msg,publicKeyBank,privateKey,publicKey)

                    


    
    except KeyboardInterrupt:
        sys.exit(0)
    
if __name__ == "__main__":
   main(sys.argv[1:])