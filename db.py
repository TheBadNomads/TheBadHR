import pyodbc 
import os

load_dotenv()

from dotenv import load_dotenv

class db:

    conn = None
    cursor = None

    @staticmethod
    async def GetDBConnection():
        if(db.conn == None):
            conn = pyodbc.connect(os.getenv("Connection_String"))

        return conn

    @staticmethod
    async def GetDBCursor():
        if(db.cursor == None):
            cursor = db.GetDBConnection().cursor()

        return cursor

    def GetUserByID(id):
        db.GetDBCursor().execute(f'SELECT * FROM [User] WHERE discord_id = {id}')
        row = db.GetDBCursor().fetchone()
        user = str(row)

        return user

    def InsertUser(first_name:str, last_name:str, discord_id:int, annual_balance:float, emergency_balance:float, sick_balance:float):
        Success = True
        try:
            db.GetDBCursor().execute(
                "INSERT INTO [User] (first_name, last_name, discord_id, annualBalance, emergencyBalance, sickBalance)"
                f"VALUES ({first_name}, {last_name}, {discord_id}, {annual_balance}, {emergency_balance}, {sick_balance});"
            )
            db.GetDBCursor().commit()
            
        except:
            db.GetDBCursor().rollback()
            Success = False

        return Success

    def InsertLeave(user_id:int, leave_type:str, days_count:float):
        Success = True
        try:
            db.GetDBCursor().execute(f'SELECT {leave_type} FROM [User] WHERE discord_id = {user_id}')
            row = db.GetDBCursor().fetchone()
            daysLeft = int(row[0])

            db.GetDBCursor().execute("UPDATE [User]"
                f"SET {leave_type} = {daysLeft - days_count}"
                f"WHERE discord_id = {user_id};"
            )
            db.GetDBCursor().commit()
            
        except:
            Success = False
            db.GetDBCursor().rollback()

        return Success
