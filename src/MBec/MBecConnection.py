import socket, os, json
from cryptography.hazmat.primitives.asymmetric import dh

current_working_directory = os.getcwd()

def sendMessage(destIP:str, destPort:int, message: str):

    userFilePath = f"{current_working_directory}/src/MBec/usersFiles/{json.loads(message.decode('utf8'))['account']}"
    if not os.path.isfile(userFilePath):
        #Execute the diffie hellman
        parameters = dh.generate_parameters(generator=2, key_size=2048)
        peer_private_key = parameters.generate_private_key()
        
    

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((destIP, destPort))
        s.sendall(message)
        data = s.recv(1024)

    return data