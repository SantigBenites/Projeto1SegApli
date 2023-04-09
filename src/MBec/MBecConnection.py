import pickle
import secrets
import socket, os, json, base64,time
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from cryptography.hazmat.primitives import hashes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Cripto import *
from MBecServerMode import receiveNewHash
#from utils import pad,unpad

current_working_directory = os.getcwd()

def sendMessage(destIP:str, destPort:int, message, privateKey, publicKeyBank, account:str,publicKey):
    
    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Start Connection
            s.connect((destIP, destPort))
            s.settimeout(3)
            
            pem = publicKey.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            #encriptação com chave publica
            messageToEncript = pickle.dumps({"account": account})
            messageEnc = encryptDataWithPublicKey(publicKeyBank,messageToEncript)
        
            messageWithPublicKey = pickle.dumps({"msg":messageEnc,"pem":pem})
            
            hashedMessage = hashMessage(messageWithPublicKey)
            
            #sends account number
            s.sendall(hashedMessage)
            
            #Authentication of MBEC
            nonceReceived = s.recv(1024) 
            
            if nonceReceived == "NOK".encode() :
                s.close()
                return None
            
            s.sendall(signwithPrivateKey(privateKey,nonceReceived))
            if(s.recv(1024).decode()!="OK"):
                s.close()
                return None
            
            
            #Authenticates Bank
            nonce = secrets.token_bytes(100)
            s.sendall(nonce)
            nounceSigned = s.recv(1024)
            #verify signature from server
            if not verifySignature(publicKeyBank,nounceSigned,nonce):
                s.sendall("NOK".encode())
                s.close()
                return None
            s.sendall("OK".encode())
            #Get EECDF shared secret
            derived_key = ephemeralEllipticCurveDiffieHellmanSending(s,privateKey, publicKeyBank)

            if derived_key == None:
                s.close()
                return None
            
            #sign message
            signature = signwithPrivateKey(privateKey,message)
            
            m = pickle.dumps({"message":message,"signature":signature})
            
            hashedMessage = hashMessage(m)

            #Setup encryption and unpadding
            iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
            cipher = AES.new(derived_key, AES.MODE_CFB,iv)
            cipherText = iv + cipher.encrypt(hashedMessage)
            
            # Send receive
            s.sendall(cipherText)
            data = s.recv(5000)

            #Setup decryption and unpadding
            # Separe iv and ciphertext
            iv = data[:AES.block_size]
            ciphertext = data[AES.block_size:]

            #Setup decryption and unpadding
            cipher = AES.new(derived_key, AES.MODE_CFB,iv)
            plaintext = cipher.decrypt(ciphertext)

            #Setup encryption and unpadding
            iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
            cipher = AES.new(derived_key, AES.MODE_CFB,iv)
            cipherText = iv + cipher.encrypt("ok".encode())

            s.sendall(cipherText)

            return plaintext
    #except (IOError, EOFError, ValueError):
    except Exception:
        s.close()
        return None
    
    
def sendMessageToStore(destIP:str, destPort:int, message: str,BankSocket):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Start Connection
            s.connect((destIP, destPort))
            s.settimeout(3)
            #Get EECDF shared secret
            derived_key = ephemeralEllipticCurveDiffieHellmanStoreSending(s)
            
            if derived_key == None:
                s.close()
                return 130
            
            #Hash Message
            hasedMessage = hashMessage(message)
            
            #Setup encryption and unpadding
            iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
            cipher = AES.new(derived_key, AES.MODE_CFB,iv)
            cipherText = iv + cipher.encrypt(hasedMessage)
            
            # Send receive
            s.sendall(cipherText)

            #autenticação mutua
            message = receiveNewHash(BankSocket,message)
            Confirmation =  message == "ok"

            data = s.recv(5000)

            #Setup decryption and unpadding
            # Separe iv and ciphertext
            iv = data[:AES.block_size]
            ciphertext = data[AES.block_size:]

            #Setup decryption and unpadding
            cipher = AES.new(derived_key, AES.MODE_CFB,iv)
            plaintext = cipher.decrypt(ciphertext)


            #Setup encryption and unpadding
            iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
            cipher = AES.new(derived_key, AES.MODE_CFB,iv)
            cipherText = iv + cipher.encrypt("ok".encode())
                
            s.sendall(cipherText)

            return plaintext if Confirmation else None
        
    except Exception:
        s.close()
        return None
        

def ephemeralEllipticCurveDiffieHellmanSending(s:socket,privateKey, publicKeyBank):

    # Creating Elliptic Curve Public Key and sending to Server
    private_key = ec.generate_private_key(ec.SECP384R1())
    public_key = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    signedPublicKey = signwithPrivateKey(privateKey,public_key)
    
    signMsg = pickle.dumps({"signedPublicKey":signedPublicKey,"public_key":public_key})

    s.sendall(hashMessage(signMsg))
    
    # Receive the server's public key
    
    enc = s.recv(1024)
    
    if enc == "NOK".encode():
        return None
    
    
    hasedMessage = pickle.loads(enc)
    
    #Verify Hash
    if "messageHashed" not in hasedMessage or "hash" not in hasedMessage:
        s.send("NOK".encode())
        return None
    
    if not verifyHash(hasedMessage):
        s.send("NOK".encode())
        return None
    
    signMessage = pickle.loads(hasedMessage["messageHashed"])
    
    if "signedPublicKey" not in signMessage or  "public_key" not in signMessage:
        s.send("NOK".encode())
        return None
    
    signed_server_public_key_bytes,server_public_key_bytes = signMessage["signedPublicKey"], signMessage["public_key"]
    server_public_key = serialization.load_pem_public_key(server_public_key_bytes)

    # Verify signature of signed_server_public_key_bytes and server_public_key_bytes with client private_key
    if not verifySignature(publicKeyBank,signed_server_public_key_bytes,server_public_key_bytes):
        s.send("NOK".encode())
        return None
    
    s.send("OK".encode())
    # Generate a shared secret
    
    shared_secret = private_key.exchange(ec.ECDH(), server_public_key)
    # Derive a key from the shared secret
    derived_key = ConcatKDFHash(
    algorithm=hashes.SHA256(),
    length=32,
    #salt=None,
    otherinfo=None
    ).derive(shared_secret)

    return derived_key


def ephemeralEllipticCurveDiffieHellmanStoreSending(s:socket):

    

    # Creating Elliptic Curve Public Key and sending to Server
    private_key = ec.generate_private_key(ec.SECP384R1())
    public_key = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo)
    s.sendall(hashMessage(public_key))

    # Receive the server's public key
    msgHash= s.recv(1024)
    
    if msgHash == "NOK".encode():
        return None
    
    hasedMessage = pickle.loads(msgHash)
    if "messageHashed" not in hasedMessage or "hash" not in hasedMessage:
        s.send("NOK".encode())
        return None
    
    if not verifyHash(hasedMessage):
        s.send("NOK".encode())
        return None
    
    server_public_key = serialization.load_pem_public_key(
    hasedMessage["messageHashed"],
    #backend=default_backend()
    )
    s.send("OK".encode())

    # Generate a shared secret
    shared_secret = private_key.exchange(ec.ECDH(), server_public_key)

    # Derive a key from the shared secret
    derived_key = ConcatKDFHash(
    algorithm=hashes.SHA256(),
    length=32,
    #salt=None,
    otherinfo=None
    ).derive(shared_secret)

    return derived_key


def sendRollBackMessage(destIP:str, destPort:int, message, privateKey, publicKeyBank, account:str,publicKey):
    
    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Start Connection
            s.connect((destIP, destPort))
            s.settimeout(3)
            
            
            pem = publicKey.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            #encriptação com chave publica
            messageToEncript = pickle.dumps({"account": account})
            messageEnc = encryptDataWithPublicKey(publicKeyBank,messageToEncript)
        
            messageWithPublicKey = pickle.dumps({"msg":messageEnc,"pem":pem})
            
            hashedMessage = hashMessage(messageWithPublicKey)
            
            #sends account number
            s.sendall(hashedMessage)
            
            #Authentication of MBEC
            nonceReceived = s.recv(1024) 
            
            if nonceReceived == "NOK".encode() :
                s.close()
                return 
            
            s.sendall(signwithPrivateKey(privateKey,nonceReceived))
            if(s.recv(1024).decode()!="OK"):
                s.close()
                return 
            
            
            #Authenticates Bank
            nonce = secrets.token_bytes(100)
            s.sendall(nonce)
            nounceSigned = s.recv(1024)
            #verify signature from server
            if not  verifySignature(publicKeyBank,nounceSigned,nonce):
                s.sendall("NOK".encode())
                s.close()
                return 
            s.sendall("OK".encode())
            #Get EECDF shared secret
            derived_key = ephemeralEllipticCurveDiffieHellmanSending(s,privateKey, publicKeyBank)

            if derived_key == None:
                return 
            
            #sign message
            signature = signwithPrivateKey(privateKey,message)
            
            m = pickle.dumps({"message":message,"signature":signature})
            
            hashedMessage = hashMessage(m)

            #Setup encryption and unpadding
            iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
            cipher = AES.new(derived_key, AES.MODE_CFB,iv)
            cipherText = iv + cipher.encrypt(hashedMessage)
            
            # Send receive
            s.sendall(cipherText)

    except Exception:
        s.close()
        return None

def sendRollBackToStore(destIP:str, destPort:int, message: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Start Connection
        s.connect((destIP, destPort))
        
        #Get EECDF shared secret
        derived_key = ephemeralEllipticCurveDiffieHellmanStoreSending(s)
        
        if derived_key == None:
            return
        
        #Hash Message
        hasedMessage = hashMessage(message)
        
        #Setup encryption and unpadding
        iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
        cipher = AES.new(derived_key, AES.MODE_CFB,iv)
        cipherText = iv + cipher.encrypt(hasedMessage)
        
        # Send receive
        s.sendall(cipherText)