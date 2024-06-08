import sqlite3

def GetBalance(login, cursor):
    cursor.execute("SELECT balance, tokens FROM main WHERE login = (?)", (login,))
    row = cursor.fetchone()
    if row == None:
        row = [-1, -1]
    return row

def RequestHandling(request):
    match(len(request)):
        case 1:
            command = request[0]
            connection = sqlite3.connect('diplomDB.db')
            cursor = connection.cursor()
            match(command):
                case "getSlotIDs":
                    cursor.execute('SELECT slotID FROM slots')
                    IDs = cursor.fetchall()
                    answer = ""
                    for ID in IDs:
                        answer += f"{ID} "
                    return answer
        case 3:
            command = request[0]
            login = request[1]
            arg = request[2]

            connection = sqlite3.connect('diplomDB.db')
            cursor = connection.cursor()

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
                case "addBalance":
                    cursor.execute('SELECT balance FROM main WHERE login = (?)',(login, ))
                    balance = cursor.fetchone()
                    if balance == None:
                        return "Not found"
                    balance = balance[0] + int(arg)
                    cursor.execute('UPDATE main SET balance = ? WHERE login = ?', (balance, login))
                    balance = f"{GetBalance(login, cursor)[0]} {GetBalance(login, cursor)[1]}"
                    connection.commit()
                    connection.close()
                    return balance
                case 'startGame':
                    slotID = args[0]
                    login = args[1]
                    cursor.execute('SELECT isActive FROM slots WHERE slotID = (?)', (slotID,))
                    status = cursor.fetchone()[0]
                    if status == 1:
                        cursor.execute('SELECT price FROM slots WHERE slotID = (?)', (slotID,))
                        price = cursor.fetchone()[0]
                        cursor.execute('SELECT balance FROM main WHERE login = (?)', (login,))
                        balance = cursor.fetchone()[0] - price
                        if balance >= 0:
                            cursor.execute('UPDATE main SET (balance, isActive) = (?, ?) WHERE login = (?)', (balance, 0, login,))
                            connection.commit()
                            connection.close()
                            return "Successful"
                        else:
                            connection.close()
                            return "Not enough money"
                    else:
                        connection.close()
                        return "Slot is busy or disabled"
        case 4:
            command = request[0]
            args = [request[1], request[2], request[3]]
            connection = sqlite3.connect('diplomDB.db')
            cursor = connection.cursor()
            match(command):
                case 'initSlot':
                    slotID = args[0]
                    isActive = args[1] == 1
                    price = args[2]
                    cursor.execute('SELECT * FROM slots WHERE slotID = (?)', (slotID,))
                    rows = cursor.fetchone()
                    if rows != None:
                        return "0"
                    cursor.execute('INSERT INTO slots (slotID, isActive, price) = (?, ?, ?)', (slotID,isActive,price,))
                    connection.commit()
                    connection.close()
                    return "1"
            



