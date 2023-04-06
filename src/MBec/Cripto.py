import hashlib
import pickle
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509

def signedMessage(response,privateKey):
    signature = signwithPrivateKey(privateKey,response)
    m = pickle.dumps({"message":response,"signature":signature})
    return m

def hashFile(filePath:str):
    file  = open(filePath, "r")
    c = file.read()
    file.close()
    return hashlib.sha256(c.encode()).hexdigest()
    

def uploadPrivateKeyToFile(privateKey, path:str):
    pem = privateKey.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    file = open(path,"wb")
    file.write(pem)
    file.close()

def readPrivateKeyFromFile(path:str):
    with open(path, "rb") as key_file:

        privateKey = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
        key_file.close()
    return privateKey

def encryptDataWithPublicKey(publicKey, message):
    return publicKey.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def getPrivateKey():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return private_key

def getPublicKey(privateKey):
    return privateKey.public_key()

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

def signwithPrivateKey(privateKey, message):
    return privateKey.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def readPublicKeyFromFile(path:str):
    with open(path, "rb") as key_file:

        public_key2 = serialization.load_pem_public_key(
            key_file.read()
        )
        key_file.close()
    return public_key2

def getPublicKeyFromCertFile(path:str):
    with open(path, "rb") as cert_file:
        cert = x509.load_pem_x509_certificate(
            cert_file.read()
        )
        cert_file.close()
    return cert.public_key()