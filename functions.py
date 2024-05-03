import sqlite3

def GetBalance(login, cursor):
    cursor.execute("SELECT balance, tokens FROM main WHERE login = (?)", (login,))
    row = cursor.fetchone()
    if row == None:
        row = [-1, -1]
    return row

def RequestHandling(request):
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
            balance = cursor.fetchone()[0]
            balance += float(arg)
            cursor.execute('UPDATE main SET balance = ? WHERE login = ?', (balance, login))
            balance = f"{GetBalance(login, cursor)[0]} {GetBalance(login, cursor)[1]}"
            connection.commit()
            connection.close()
            return balance
