import socket

def receiveConnection(host="127.0.0.1",port=3000):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()
        print(f"Connected by {addr}")

    return (conn,addr)


def receiveMessage(connection:socket):

    return connection.recv(1024)

def sendMessage(connection:socket,data):

    connection.sendall(data)