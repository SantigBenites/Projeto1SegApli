import socket
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from cryptography.hazmat.primitives import hashes
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad


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

    #Setup encryption and unpadding
    iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
    cipher = AES.new(derived_key, AES.MODE_CFB,iv)
    cipherText = iv + cipher.encrypt(data)

    connection.sendall(cipherText)
    
def sendMessageToBank(destIP:str, destPort:int, message: str):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        # Start Connection
        s.connect((destIP, destPort))

        #Get EECDF shared secret
        derived_key = ephemeralEllipticCurveDiffieHellmanSending(s)

        #Setup encryption and unpadding
        iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
        cipher = AES.new(derived_key, AES.MODE_CFB,iv)
        cipherText = iv + cipher.encrypt(message)
        
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


def ephemeralEllipticCurveDiffieHellmanSending(s:socket):

    

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