import hashlib
import pickle
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509

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