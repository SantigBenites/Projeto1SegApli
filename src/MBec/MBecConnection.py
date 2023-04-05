import socket, os, json, base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from cryptography.hazmat.primitives import hashes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
#from utils import pad,unpad

current_working_directory = os.getcwd()

def sendMessage(destIP:str, destPort:int, message: str):
    

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        
        # Start Connection
        s.connect((destIP, destPort))

        #Get EECDF shared secret
        derived_key = ephemeralEllipticCurveDiffieHellmanSending(s)

        #Setup encryption and unpadding
        cipher = AES.new(derived_key, AES.MODE_CFB,bytes([16])*16)
        cipherText = cipher.encrypt(message)
        # Send receive
        s.send(cipherText)
        data = s.recv(5000)

        #Setup decryption and unpadding
        cipher = AES.new(key=derived_key, mode=AES.MODE_CFB,iv=bytes([16])*16)
        plaintext = cipher.decrypt(data)


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
