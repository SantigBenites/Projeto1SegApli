import secrets
import socket
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from cryptography.hazmat.primitives import hashes
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from Cripto import *


# Generate an ephemeral elliptic curve key pair
private_key = ec.generate_private_key(ec.SECP384R1())

# Serialize the public key for sending to the client
public_key = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

def createSocket(host="127.0.0.1",port=5000):
    
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    return s

def receiveNewConnection(socket:socket.socket):
    
    socket.listen()
    conn, addr = socket.accept()    
    return (conn,addr)

def receiveMessage(connection:socket):
    #Get EECDF shared secret
    derived_key = ephemeralEllipticCurveDiffieHellmanReceiving(connection)
    
    if derived_key == None:
        connection.close()
        return None

    # Receive cyphertext from client
    data = connection.recv(5000)

    #Setup decryption and unpadding
    # Separe iv and ciphertext
    iv = data[:AES.block_size]
    ciphertext = data[AES.block_size:]
    cipher = AES.new(key=derived_key, mode=AES.MODE_CFB,iv=iv)
    plaintext = cipher.decrypt(ciphertext)

    return plaintext,derived_key

def sendMessage(connection:socket,data,derived_key):
    
    hashedMessage = hashMessage(data)

    #Setup encryption and unpadding
    iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
    cipher = AES.new(derived_key, AES.MODE_CFB,iv)
    cipherText = iv + cipher.encrypt(hashedMessage)

    connection.sendall(cipherText)
    
def sendMessageToBank(destIP:str, destPort:int, message: str,publicKeyBank,privateKey,publicKey):
    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            
            # Start Connection
            s.connect((destIP, destPort))
            
            pem = publicKey.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            #encriptação com chave publica
            messageToEncript = pickle.dumps({"account": ""})
            messageEnc = encryptDataWithPublicKey(publicKeyBank,messageToEncript)
        
            messageWithPublicKey = pickle.dumps({"msg":messageEnc,"pem":pem})
            
            hashedMessage = hashMessage(messageWithPublicKey)
            
            #sends account number
            s.sendall(hashedMessage)
            
            #Authentication of MBEC
            nonceReceived = s.recv(1024) 
            
            #if nonceReceived == "NOK".encode() :
            #    return None
                
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
                #s.sendall("NOK".encode())
                s.close()
                return None
            s.sendall("OK".encode())
            #Get EECDF shared secret
            derived_key = ephemeralEllipticCurveDiffieHellmanSending(s,privateKey,publicKeyBank)

            if derived_key == None:
                s.close()
                return None
            
            #Setup encryption and unpadding
            iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
            cipher = AES.new(derived_key, AES.MODE_CFB,iv)
            
            #hashMessage
            hasedMessage = hashMessage(message)
            
            cipherText = iv + cipher.encrypt(hasedMessage)
            
            # Send receive
            s.send(cipherText)
            data = s.recv(5000)

            #Setup decryption and unpadding
            # Separe iv and ciphertext
            iv = data[:AES.block_size]
            ciphertext = data[AES.block_size:]

            #Setup decryption and unpadding
            cipher = AES.new(derived_key, AES.MODE_CFB,iv)
            plaintext = cipher.decrypt(ciphertext)
            return plaintext
    except socket.error:
                return None

def ephemeralEllipticCurveDiffieHellmanSending(s:socket,privateKey, publicKeyBank):

    

    # Creating Elliptic Curve Public Key and sending to Server
    private_key = ec.generate_private_key(ec.SECP384R1())
    public_key = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    signedPublicKey = signwithPrivateKey(privateKey,public_key)
    signedMsg = pickle.dumps({"signedPublicKey":signedPublicKey,"public_key":public_key})
    
    s.sendall(hashMessage(signedMsg))
    enc = s.recv(1024)
    if enc == "NOK".encode():
        return None

    hasedMessage = pickle.loads(enc)
    
    
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


def ephemeralEllipticCurveDiffieHellmanReceiving(connection):

    # Creating Elliptic Curve Public Key 
    private_key = ec.generate_private_key(ec.SECP384R1())
    public_key = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Receive the client's public key
    msgHash= connection.recv(1024)
    
    hasedMessage = pickle.loads(msgHash)
    if "messageHashed" not in hasedMessage or "hash" not in hasedMessage:
        connection.send("NOK".encode())
        return None
    
    if not verifyHash(hasedMessage):
        connection.send("NOK".encode())
        return None
    
    client_public_key = serialization.load_pem_public_key(
        hasedMessage["messageHashed"],
        #backend=default_backend()
    )


    # Generate a shared secret
    shared_secret = private_key.exchange(ec.ECDH(), client_public_key)

    # Derive a key from the shared secret
    derived_key = ConcatKDFHash(
        algorithm=hashes.SHA256(),
        length=32,
        #salt=None,
        otherinfo=None
    ).derive(shared_secret)

    # Send the server's public key to the client
    connection.sendall(hashMessage(public_key))
   
    if connection.recv(1024) == "NOK".encode():
        return None

    return derived_key



def sendRollBackToBank(destIP:str, destPort:int, message: str,publicKeyBank,privateKey,publicKey):
        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        # Start Connection
        s.connect((destIP, destPort))
        
        pem = publicKey.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        #encriptação com chave publica
        messageToEncript = pickle.dumps({"account": ""})
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
        derived_key = ephemeralEllipticCurveDiffieHellmanSending(s,privateKey,publicKeyBank)

        if derived_key == None:
            s.close()
            return 
        
        #Setup encryption and unpadding
        iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
        cipher = AES.new(derived_key, AES.MODE_CFB,iv)
        
        #hashMessage
        hasedMessage = hashMessage(message)
        
        cipherText = iv + cipher.encrypt(hasedMessage)
        
        # Send receive
        s.send(cipherText)