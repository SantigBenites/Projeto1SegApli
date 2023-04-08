import socket,base64
from Crypto.Cipher import AES
from Cripto import *
from MBecConnection import *

def createSocket(host="127.0.0.1"):

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(10)
    s.bind((host, 0))
    return s, s.getsockname()[0], s.getsockname()[1]

def receiveNewHash(s:socket.socket,message:str):


    s.listen()
    try:
        # Accept new bank connection
        while True:
            conn, addr = s.accept()

            # Obtain derived key from diffie hellman
            derived_key = ServerModeDiffieHellman(conn)

            # Receive cyphertext
            cipherText = conn.recv(5000)
            # Separe iv and ciphertext
            iv = cipherText[:AES.block_size]
            ciphertext = cipherText[AES.block_size:]

            #Setup decryption and unpadding
            cipher = AES.new(derived_key, AES.MODE_CFB,iv)
            receivedMessage = cipher.decrypt(ciphertext)

            receivedHash = pickle.loads(receivedMessage)["hashFile"]

            originalHah =  hashlib.sha256(message).hexdigest()

            if receivedHash == originalHah:
                # Send ok to bank
                #Setup decryption and unpadding
                iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
                cipher = AES.new(key=derived_key, mode=AES.MODE_CFB, iv=iv)
                cipherText = iv + cipher.encrypt("OK".encode("utf-8"))
                conn.sendall(cipherText)
                conn.close()

                return "ok"
    except socket.timeout:
        s.close()
        return None

def ServerModeDiffieHellman(connection):

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
        return None
    
    if not verifyHash(hasedMessage):
        return None
    
    client_public_key = serialization.load_pem_public_key(
        hasedMessage["messageHashed"]
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

    return derived_key