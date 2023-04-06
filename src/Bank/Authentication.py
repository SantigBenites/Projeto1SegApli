import secrets
import socket
from Cripto import *
from BankConnection import *


def authentication (message,conn:socket,privateKey):
    
    account = message["account"]
    publicKey = message["publicKey"].encode()
    
    
    #generates randombytes
    s  = secrets.token_bytes(100)
    sendMessage(s)
    
    signedMessage = conn.recv(1024)
    b = verifySignature(publicKey,signedMessage,s)
    
    if not b:
        return False
    
    s.sendall("OK".encode())
    
    nonce = s.recv(1024)
    signedMessage = signwithPrivateKey(privateKey,nonce)
    s.sendall(signedMessage)
    
    
    return True