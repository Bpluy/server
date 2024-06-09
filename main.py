import socket
from functions import *

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
IP = "0.0.0.0"
PORT = 11333
listener.bind((IP,PORT))
listener.listen(0)

#connection, address = listener.accept()

#connection.send("Подключение успешно!".encode('utf8'))

while True:
    connection, address = listener.accept()
    connection.send("Successfull".encode('utf8'))
    request = decrypt_string(connection.recv(1024)).split(" ")
    print(request)
    answer = RequestHandling(request)
    connection.send(answer.encode('utf8'))
    connection.close()
