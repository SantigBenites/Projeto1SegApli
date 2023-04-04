
import datetime
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import cryptography
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization


def hashFile(filePath:str):
    file  = open(filePath, "r")
    c = file.read()
    file.close()
    return hashlib.sha256(c.encode()).hexdigest()


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
    
def encryptDataWithPublicKey(publicKey, message):
    return publicKey.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
def decryptWithPrivateKey(privatekey,cipherText):
    
    return privatekey.decrypt(
            cipherText,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    
def uploadPublicKeyToFile(publickey,path:str):
    pem = publickey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    file = open(path,"wb")
    file.write(pem)
    file.close()
    print("created")
    
def readPublicKeyFromFile(path:str):
    with open("auth", "rb") as key_file:

        public_key2 = serialization.load_pem_public_key(
            key_file.read()
        )
        key_file.close()
    return public_key2

def generateSelfSignedCert(privateKey, path:str):
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"PT"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Lisbon"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company")
    ])

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        privateKey.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=10)
    ).sign(privateKey, hashes.SHA256())
    
    with open(path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print("created")
        
    return cert
    
def getPublicKeyFromCertFile(path:str):
    with open(path, "rb") as cert_file:
        cert = x509.load_pem_x509_certificate(
            cert_file.read()
        )
        cert_file.close()
    return cert.public_key()
    
    