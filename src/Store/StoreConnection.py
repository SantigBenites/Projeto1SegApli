import socket


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
    return connection.recv(1024)

def sendMessage(connection:socket,data):
    connection.sendall(data)
    
def sendMessageToBank(destIP:str, destPort:int, message: str):
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((destIP, destPort))
        s.sendall(message)
        data = s.recv(1024)

    return data