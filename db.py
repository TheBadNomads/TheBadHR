import pyodbc 
import os

load_dotenv()

from dotenv import load_dotenv

class db:

    conn = None
    cursor = None

    @staticmethod
    def GetDBConnection():
        if(db.conn == None):
            conn = pyodbc.connect(os.getenv("Connection_String"))

        return conn

    @staticmethod
    def GetDBCursor():
        if(db.cursor == None):
            cursor = db.GetDBConnection().cursor()

        return cursor

