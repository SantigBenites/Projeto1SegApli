import socket,base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from cryptography.hazmat.primitives import hashes
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from Cripto import *
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
    #autenticação servidor
    
    nounce = conn.recv(1024)
    
    nounceSigned = signwithPrivateKey(privateKey,nounce)
    
    conn.sendall(nounceSigned)
    
    
    #recebe nonce do cliente
    #bank assina
    #cliente 
    #
    return (conn,addr)



def receiveMessage(connection:socket):

    #Get EECDF shared secret
    derived_key = ephemeralEllipticCurveDiffieHellmanReceiving(connection)

    # Receive cyphertext from client
    cipherText = connection.recv(5000)
 
    #Setup decryption and unpadding
    cipher = AES.new(derived_key, AES.MODE_CFB,bytes([16])*16)
    plaintext = cipher.decrypt(cipherText)

    return plaintext,derived_key

def sendMessage(connection:socket,data,derived_key):

    #Setup decryption and unpadding
    cipher = AES.new(key=derived_key, mode=AES.MODE_CFB, iv=bytes([16])*16)
    ciphertext = cipher.encrypt(data)

    connection.sendall(ciphertext)


def ephemeralEllipticCurveDiffieHellmanReceiving(connection):

    # Creating Elliptic Curve Public Key 
    private_key = ec.generate_private_key(ec.SECP384R1())
    public_key = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Receive the client's public key
    client_public_key_bytes = connection.recv(1024)
    client_public_key = serialization.load_pem_public_key(
        client_public_key_bytes,
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
    connection.sendall(public_key)

    return derived_key