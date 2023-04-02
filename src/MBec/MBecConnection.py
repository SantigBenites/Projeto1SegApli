import socket

def sendMessage(destIP:str, destPort:int, message: str):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((destIP, destPort))
        s.sendall(message)
        data = s.recv(1024)

    return data