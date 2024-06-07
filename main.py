import socket
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from functions import *

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
IP = "0.0.0.0"
print(IP)
PORT = 11333
listener.bind((IP,PORT))
listener.listen(0)
key = base64.b64decode("LPjR6pHBsx2VvuYNYAaRZfGKsomvqsh3vAODL46dENw=")
iv = base64.b64decode("nXJhi/OyX83gULxJv1UARQ==")

def decrypt_string(cipher_text):
    cipher_text = cipher_text.decode('utf-8')
    cipher_text = base64.b64decode(cipher_text)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plain_text = decryptor.update(cipher_text) + decryptor.finalize()
    return plain_text.decode('utf-8')

#connection, address = listener.accept()

#connection.send("Подключение успешно!".encode('utf8'))

while True:
    connection, address = listener.accept()
    connection.send("Successfull".encode('utf8'))
    request = decrypt_string(connection.recv(1024)).split(" ")
    answer = RequestHandling(request)
    connection.send(answer.encode('utf8'))
    connection.close()
