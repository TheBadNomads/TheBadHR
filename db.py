import pyodbc 
import os

def load_db():
    global conn 
    global cursor 

    conn = pyodbc.connect(os.getenv("Connection_String"))
    cursor = conn.cursor()


def GetUserByID(id):
    cursor.execute(f'SELECT * FROM [User] WHERE discord_id = {id}')
    row = cursor.fetchone()
    user = str(row)

    return user

def InsertUser(first_name:str, last_name:str, discord_id:int, annual_balance:float, emergency_balance:float, sick_balance:float):
    Success = True
    try:
        cursor.execute(
            "INSERT INTO [User] (first_name, last_name, discord_id, annualBalance, emergencyBalance, sickBalance)"
            f"VALUES ({first_name}, {last_name}, {discord_id}, {annual_balance}, {emergency_balance}, {sick_balance});"
        )
        
    except:
        Success = False

    if Success:
        conn.commit()
    else:
        conn.rollback()

    return Success

def ApplyLeave(user_id:int, leave_type:str, days_count:float):
    Success = True
    try:
        cursor.execute(f'SELECT {leave_type} FROM [User] WHERE discord_id = {user_id}')
        row = cursor.fetchone()
        daysLeft = int(row[0])

        cursor.execute("UPDATE [User]"
            f"SET {leave_type} = {daysLeft - days_count}"
            f"WHERE discord_id = {user_id};"
        )
        
    except:
        Success = False

    if Success:
        conn.commit()
    else:
        conn.rollback()

    return Success
