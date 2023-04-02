import socket

def createSocket(host="127.0.0.1",port=3000):

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