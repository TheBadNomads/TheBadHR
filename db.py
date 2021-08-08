import pyodbc 
import os

def load_db():
    global conn 
    global cursor 

    conn= pyodbc.connect(os.getenv("Connection_String"))
    cursor= conn.cursor()


def GetUserByID(id):
    cursor.execute(f'SELECT * FROM [User] WHERE discord_id = {id}')
    row= cursor.fetchone()
    user= str(row)

    return user

def InsertUser(first_name:str, last_name:str, discord_id:int, annualBalance:float, emergencyBalance:float, sickBalance:float):
    error= False
    try:
        cursor.execute(
            "INSERT INTO [User] (first_name, last_name, discord_id, annualBalance, emergencyBalance, sickBalance)"
            f"VALUES ({first_name}, {last_name}, {discord_id}, {annualBalance}, {emergencyBalance}, {sickBalance});"
        )
        
    except:
        error= True

    if not error:
        conn.commit()
    else:
        conn.rollback()

    return error

def ApplyLeave(user_id:int, leaveType:str, daysAmount:float):
    error= False
    try:
        cursor.execute(f'SELECT {leaveType} FROM [User] WHERE discord_id = {user_id}')
        row= cursor.fetchone()
        daysLeft= int(row[0])

        cursor.execute("UPDATE [User]"
            f"SET {leaveType} = {daysLeft-daysAmount}"
            f"WHERE discord_id = {user_id};"
        )
        
    except:
        error= True

    if not error:
        conn.commit()
    else:
        conn.rollback()

    return error
