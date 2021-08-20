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
            db.conn = pyodbc.connect(os.getenv("Connection_String"))

        return db.conn

    @staticmethod
    def GetDBCursor():
        if(db.cursor == None):
            db.cursor = db.GetDBConnection().cursor()

        return db.cursor

