import sqlite3
import socket
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

def GetBalance(login, cursor):
    cursor.execute("SELECT balance, tokens FROM main WHERE login = (?)", (login,))
    row = cursor.fetchone()
    if row == None:
        row = [-1, -1]
    return row

def RequestHandling(request):
    connection = sqlite3.connect('diplomDB.db')
    cursor = connection.cursor()

    match(len(request)):
        case 1:
            command = request[0]

            match(command):
                case "getSlotIDs":
                    cursor.execute('SELECT slotID FROM slots')
                    IDs = cursor.fetchall()
                    answer = ""
                    for ID in IDs:
                        answer += f"{ID[0]} "
                    return answer
        case 2:
            command = request[0]
            arg = request[1]

            match(command):
                case "changeSlotState":
                    cursor.execute('SELECT isActive FROM slots WHERE slotID = (?)', (arg,))
                    state = cursor.fetchone()[0]
                    state = (state + 1) % 2
                    cursor.execute('UPDATE slots SET isActive = (?) WHERE slotID = (?)', (state, arg,))
                    connection.commit()
                    connection.close()
                    return f"{state}"
                case "checkBalance":
                    cursor.execute('SELECT balance, tokens FROM main WHERE login = (?)', (arg,))
                    balance = cursor.fetchone()
                    message = f"{balance[0]} {balance[1]}"
                    connection.close()
                    return message
                case "checkSlotName":
                    cursor.execute('SELECT name FROM slots WHERE slotID = (?)', (arg,))
                    name = cursor.fetchone()[0]
                    connection.close()
                    return name
        case 3:
            command = request[0]
            login = request[1]
            arg = request[2]

            match(command):
                case "login":
                    cursor.execute('SELECT * FROM main WHERE (login, password) = (?, ?)',(login, arg))
                    rows = cursor.fetchone()
                    balance = f"{GetBalance(login, cursor)[0]} {GetBalance(login, cursor)[1]}"
                    connection.close()
                    if rows != None:
                        return f"1 {balance}"
                    else:
                        return "0"
                case "register":
                    cursor.execute('SELECT * FROM main WHERE (login, password) = (?, ?)',(login, arg))
                    rows = cursor.fetchone()
                    if rows != None:
                        return "0"
                    cursor.execute('INSERT INTO main (login, password, balance, tokens) VALUES (?, ?, 0, 0)',(login, arg))
                    balance = f"{GetBalance(login, cursor)[0]} {GetBalance(login, cursor)[1]}"
                    connection.commit()
                    connection.close()
                    return "1"
                case "addTokens":
                    cursor.execute('SELECT tokens FROM main WHERE login = (?)',(login, ))
                    tokens = cursor.fetchone()[0]
                    tokens += int(arg)
                    cursor.execute('UPDATE main SET tokens = ? WHERE login = ?', (tokens, login))
                    balance = f"{GetBalance(login, cursor)[0]} {GetBalance(login, cursor)[1]}"
                    connection.commit()
                    connection.close()
                    return balance
                case "spendTokens":
                    cursor.execute('SELECT tokens FROM main WHERE login = (?)',(login, ))
                    tokens = cursor.fetchone()[0]
                    if tokens == None:
                        return "Incorrect login"
                    if tokens < int(arg):
                        return f"Not enough tokens;{tokens}"
                    tokens -= int(arg)
                    cursor.execute('UPDATE main SET tokens = ? WHERE login = ?', (tokens, login))
                    balance = f"{GetBalance(login, cursor)[0]} {GetBalance(login, cursor)[1]}"
                    connection.commit()
                    connection.close()
                    return balance
                case "addBalance":
                    cursor.execute('SELECT balance FROM main WHERE login = (?)',(login, ))
                    balance = cursor.fetchone()
                    if balance == None:
                        return "Not found"
                    balance = balance[0] + int(arg)
                    cursor.execute('UPDATE main SET balance = (?) WHERE login = (?)', (balance, login))
                    balance = f"{GetBalance(login, cursor)[0]} {GetBalance(login, cursor)[1]}"
                    connection.commit()
                    connection.close()
                    return balance
                case 'startGame':
                    slotID = request[1]
                    login = request[2]
                    cursor.execute('SELECT isActive FROM slots WHERE slotID = (?)', (slotID,))
                    status = cursor.fetchone()[0]
                    if status == 1:
                        cursor.execute('SELECT price FROM slots WHERE slotID = (?)', (slotID,))
                        price = cursor.fetchone()[0]
                        cursor.execute('SELECT balance FROM main WHERE login = (?)', (login,))
                        balance = cursor.fetchone()[0] - price
                        if balance >= 0:
                            cursor.execute('UPDATE main SET balance = (?) WHERE login = (?)', (balance, login,))
                            connection.commit()
                            cursor.execute('UPDATE slots SET isActive = (?) WHERE slotID = (?)', (0,slotID,))
                            connection.commit()
                            con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            con.connect(("95.174.93.97",11334))
                            rd = con.recv(1024)
                            message = encrypt_string(f"{login}")
                            con.send(message.encode('utf8'))
                            rd = con.recv(1024).decode('utf8')
                            token = int(rd)
                            cursor.execute('SELECT tokens FROM main WHERE login = (?)', (login,))
                            tokens = token + cursor.fetchone()[0]
                            cursor.execute('UPDATE main SET tokens = (?) WHERE login = (?)', (tokens,login,))
                            connection.commit()
                            cursor.execute('UPDATE slots SET isActive = (?) WHERE slotID = (?)', (1,slotID,))
                            connection.commit()
                            connection.close()
                            return f"{token}"
                        else:
                            connection.close()
                            return "Not enough money"
                    else:
                        connection.close()
                        return "Slot is busy or disabled"
        case 5:
            command = request[0]
            args = [request[1], request[2], request[3], request[4]]

            match(command):
                case 'initSlot':
                    slotID = args[0]
                    isActive = int(args[1])
                    price = int(args[2])
                    name = args[3]
                    cursor.execute('SELECT * FROM slots WHERE slotID = (?)', (slotID,))
                    rows = cursor.fetchone()
                    if rows != None:
                        return "0"
                    cursor.execute('INSERT INTO slots (slotID, isActive, price, name) VALUES (?, ?, ?, ?)', (slotID,isActive,price,name,))
                    connection.commit()
                    connection.close()
                    return "1"

def encrypt_string(plain_text):
    key = base64.b64decode("LPjR6pHBsx2VvuYNYAaRZfGKsomvqsh3vAODL46dENw=")
    iv = base64.b64decode("nXJhi/OyX83gULxJv1UARQ==")
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plain_text.encode('utf-8')) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()
    
    return base64.b64encode(encrypted_bytes).decode('utf-8')
                
def decrypt_string(cipher_text):
    key = base64.b64decode("LPjR6pHBsx2VvuYNYAaRZfGKsomvqsh3vAODL46dENw=")
    iv = base64.b64decode("nXJhi/OyX83gULxJv1UARQ==")
    cipher_text = cipher_text.decode('utf-8')
    cipher_text = base64.b64decode(cipher_text)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    plain_text = decryptor.update(cipher_text) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plain_text = unpadder.update(plain_text) + unpadder.finalize()
    return plain_text.decode('utf-8')