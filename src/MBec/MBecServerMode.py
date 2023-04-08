import socket,base64
from Cripto import *
from MBecConnection import *

def createSocket(host="127.0.0.1"):

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, 0))
    return s, s.getsockname()[1]

def receiveNewHash(socket:socket.socket,vccFilePath:str):


    socket.listen()
    
    while True:
        # Accept new bank connection
        conn, addr = socket.accept()

        # Obtain derived key from diffie hellman
        derived_key = ServerModeDiffieHellman(conn)

        # Receive cyphertext
        cipherText = conn.recv(5000)
        # Separe iv and ciphertext
        iv = cipherText[:AES.block_size]
        ciphertext = cipherText[AES.block_size:]

        #Setup decryption and unpadding
        cipher = AES.new(derived_key, AES.MODE_CFB,iv)
        receivedHash = cipher.decrypt(ciphertext)

        originalHah = hashFile(vccFilePath)

        if receivedHash == originalHah:
            conn.close()
            # Send ok to bank
            #Setup decryption and unpadding
            iv = AES.new(key=derived_key, mode=AES.MODE_CFB).iv
            cipher = AES.new(key=derived_key, mode=AES.MODE_CFB, iv=iv)
            cipherText = iv + cipher.encrypt("OK")
            return 
        
        conn.close()

def ServerModeDiffieHellman(connection):

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