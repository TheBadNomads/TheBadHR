from datetime import datetime
import pyodbc 
import os

def load_db():
    global conn 
    global cursor 

    conn = pyodbc.connect(os.getenv("Connection_String"))
    cursor = conn.cursor()


def GetUserByID(id):
    cursor.execute(f'SELECT * FROM [User] WHERE discord_id = {id}')
    user = cursor.fetchone()

    return user

def GetLeaveBalance(id, leaveType):
    leaveTypes = {
        1: "annualBalance",
        2: "emergencyBalance",
        3: "sickBalance"
    }

    cursor.execute(f'SELECT {leaveTypes[leaveType]} FROM [User] WHERE discord_id = {id}')
    row = cursor.fetchone()
    balance = row[0]

    return balance

def GetLeaveByID(request_id):
    cursor.execute(f'SELECT * FROM [Leaves] WHERE request_id = {request_id}')
    row = cursor.fetchone()
    leave = row

    return leave

def GetLeaveStatus(request_id):
    cursor.execute(f'SELECT leave_status FROM [Leaves] WHERE request_id = {request_id}')
    row = cursor.fetchone()
    leave_status = str(row[0])

    return leave_status

def InsertUser(first_name:str, last_name:str, discord_id:int, annualBalance:float, emergencyBalance:float, sickBalance:float):
    error = False
    try:
        cursor.execute(
            "INSERT INTO [User] (first_name, last_name, discord_id, annualBalance, emergencyBalance, sickBalance) VALUES (?, ?, ?, ?, ?, ?)",
            (first_name, last_name, discord_id, annualBalance, emergencyBalance, sickBalance)
        )
        
    except:
        error = True

    if not error:
        conn.commit()

    else:
        conn.rollback()
    
    return error

def InsertLeave(user_id:int, leave_type:int, request_id:int, leave_status:str, start_date:str, end_date: str, requested_days:float):
    error = False
    try:
        cursor.execute(
            "INSERT INTO [Leaves] (user_id, leave_type, request_id, leave_status, start_date, end_date, requested_days) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, leave_type, request_id, leave_status, datetime.strptime(start_date, '%m/%d/%Y'), datetime.strptime(end_date, '%m/%d/%Y'), requested_days)
        )
        
    except Exception as e:
        print(e)
        error = True

    if not error:
        conn.commit()

    else:
        conn.rollback()

    return error

def UpdateLeaveStatus(request_id, leave_status):
    error= False
    try:
        cursor.execute("UPDATE [Leaves] SET leave_status = ? WHERE request_id = ?", leave_status, request_id)
        
    except:
        error= True

    if not error:
        conn.commit()
    else:
        conn.rollback()

    return error

def UpdateLeaveBalance(user_id, leave_type, requested_days):
    error = False
    leaveTypes = {
        1: "annualBalance",
        2: "emergencyBalance",
        3: "sickBalance"
    }

    try:
        cursor.execute(f"UPDATE [User] SET {leaveTypes[leave_type]} = {leaveTypes[leave_type]} + ? WHERE id = ?", requested_days, user_id)
        
    except:
        error = True

    if not error:
        conn.commit()
    else:
        conn.rollback()

    return error