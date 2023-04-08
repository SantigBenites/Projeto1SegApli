import secrets
import socket,base64, hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from cryptography.hazmat.primitives import hashes
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from Cripto import *
from BankStorage import *
#from utils import pad,unpad

# Generate an ephemeral elliptic curve key pair
private_key = ec.generate_private_key(ec.SECP384R1())

# Serialize the public key for sending to the client
public_key = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

from cryptography import x509

def createSocket(host="127.0.0.1",port=3000):

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen()
    return s

def receiveNewConnection(socket:socket.socket,privateKey):


    socket.listen()
    
    conn, addr = socket.accept()
    
    #recebe {account,chavepublica}
    received = conn.recv(5000)
    hasedMessage =  pickle.loads(received)
    
    if "messageHashed" not in hasedMessage or "hash" not in hasedMessage:
        return
    
    if not verifyHash(hasedMessage):
        return
    
    receivedmsg = pickle.loads(hasedMessage["messageHashed"])
    
    if "msg" not in receivedmsg or "pem" not in receivedmsg:
        return
    
    encriptedMsg = receivedmsg["msg"]
    publicKeyBytes = receivedmsg["pem"]
    decripted = decryptWithPrivateKey(privateKey,encriptedMsg)
    accountNumber = pickle.loads(decripted)
    
    store = BankStorageSingleton()
    
    publicKeyUser = store.getPublicKeyUser(accountNumber["account"])
    
    if publicKeyUser == None :
        publicKeyUser = serialization.load_pem_public_key(publicKeyBytes)
        
    #Authentication of MBEC
    nonce = secrets.token_bytes(100)
    conn.sendall(nonce)
    signedNonce = conn.recv(1024)
    if not verifySignature(publicKeyUser,signedNonce,nonce):
        conn.sendall("NOK".encode())
        conn.close()
    
    conn.sendall("OK".encode())
    

    #Bank Authentication
    nounce = conn.recv(1024)
    nounceSigned = signwithPrivateKey(privateKey,nounce)
    conn.sendall(nounceSigned)
    
    if(conn.recv(1024).decode()!="OK"):
        conn.close()
        return
    
    return (conn,addr,accountNumber["account"],publicKeyUser)


def receiveMessage(connection:socket,PublicKeyClient,privateKey):

    #Get EECDF shared secret
    derived_key = ephemeralEllipticCurveDiffieHellmanReceiving(connection,PublicKeyClient,privateKey)

    # Receive cyphertext from client
    cipherText = connection.recv(5000)

    # Separe iv and ciphertext
    iv = cipherText[:AES.block_size]
    ciphertext = cipherText[AES.block_size:]

    #Setup decryption and unpadding
    cipher = AES.new(derived_key, AES.MODE_CFB,iv)
    plaintext = cipher.decrypt(ciphertext)

    return plaintext,derived_key

def sendMessage(connection:socket,data,derived_key):

    #Setup decryption and unpadding
    iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
    cipher = AES.new(key=derived_key, mode=AES.MODE_CFB, iv=iv)
    cipherText = iv + cipher.encrypt(data)

    connection.sendall(cipherText)


def ephemeralEllipticCurveDiffieHellmanReceiving(connection,PublicKeyClient,privateKey):

    # Creating Elliptic Curve Public Key 
    private_key = ec.generate_private_key(ec.SECP384R1())
    public_key = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    signedPublicKey = signwithPrivateKey(privateKey,public_key)

    # Receive the client's public key signed with PEIVATE Key that match priviously send PublickeY
    receivedMessage = pickle.loads(connection.recv(5000))
    signed_client_public_key_bytes,client_public_key_bytes = receivedMessage["signedPublicKey"], receivedMessage["public_key"]
    client_public_key = serialization.load_pem_public_key(client_public_key_bytes)
    
    # Verify signature of signed_client_public_key and client_public_key with server private_key 
    if not verifySignature(PublicKeyClient,signed_client_public_key_bytes,client_public_key_bytes):
        return None

    # Generate a shared secret
    shared_secret = private_key.exchange(ec.ECDH(), client_public_key)

    # Derive a key from the shared secret
    derived_key = ConcatKDFHash(
        algorithm=hashes.SHA256(),
        length=32,
        #salt=None,
        otherinfo=None
    ).derive(shared_secret)

    # Send the server's public key and signed public key to the client
    connection.sendall(pickle.dumps({"signedPublicKey":signedPublicKey,"public_key":public_key}))

    return derived_key


def ClientMode(ip:str,port:int,hashFile):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
        # Start Connection
            s.connect((ip,port))
        except socket.error:
            return None
        # Do the diffie Hellman
        derived_key = ClientModeDiffieHellman(s)
                  
        #Setup encryption and unpadding
        iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
        cipher = AES.new(derived_key, AES.MODE_CFB,iv)
        cipherText = iv + cipher.encrypt(pickle.dumps({"hashFile":hashFile}))

        # Send to client
        s.sendall(cipherText)
        data = s.recv(5000)

        #Setup decryption and unpadding
        # Separe iv and ciphertext
        iv = data[:AES.block_size]
        ciphertext = data[AES.block_size:]

        #Setup decryption and unpadding
        cipher = AES.new(derived_key, AES.MODE_CFB,iv)
        plaintext = cipher.decrypt(ciphertext)

    return plaintext.decode()




def ClientModeDiffieHellman(s:socket):

    # Creating Elliptic Curve Public Key and sending to Server
    private_key = ec.generate_private_key(ec.SECP384R1())
    public_key = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo)
    s.sendall(public_key)

    # Receive the server's public key
    server_public_key_bytes = s.recv(1024)
    server_public_key = serialization.load_pem_public_key(
    server_public_key_bytes,
    #backend=default_backend()
    )

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