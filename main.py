import socket
from functions import *

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
IP = "95.174.93.97"
PORT = 11333
listener.bind((IP,PORT))
listener.listen(0)

#connection, address = listener.accept()

#connection.send("Подключение успешно!".encode('utf8'))

while True:
    connection, address = listener.accept()
    connection.send("Successfull".encode('utf8'))
    request = decrypt_string(connection.recv(1024)).split(" ")
    answer = RequestHandling(request)
    connection.send(answer.encode('utf8'))
    connection.close()
