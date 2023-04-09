import hashlib
import datetime
import pickle
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509

def getTimeStamp():
    dt = datetime.datetime.now()
    return datetime.datetime.timestamp(dt)

def verifyTimeStampValidity(ClientTimeStamp):
    dt = getTimeStamp()
    #10 min
    return (dt-ClientTimeStamp) < 600


def hashMessage (message):
    hashMsg  = hashlib.sha256(message).hexdigest()
    return pickle.dumps({"messageHashed":message,"hash": hashMsg })

def verifyHash (message):
    receivedHash = message["hash"]
    hashObtained = hashlib.sha256(message["messageHashed"]).hexdigest()
    return receivedHash == hashObtained

def verifySignature(publicKey, signature, message):
    try:
        publicKey.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
            )
    except cryptography.exceptions.InvalidSignature:
        print("Invalide signature")
        return False
    return True

def getPublicKeyFromCertFile(path:str):
    with open(path, "rb") as cert_file:
        cert = x509.load_pem_x509_certificate(
            cert_file.read()
        )
        cert_file.close()
    return cert.public_key()


def signwithPrivateKey(privateKey, message):
    return privateKey.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
def getPrivateKey():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return private_key

def getPublicKey(privateKey):
    return privateKey.public_key()

def encryptDataWithPublicKey(publicKey, message):
    return publicKey.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )