import pyodbc 
import os

def load_db():
    global conn 
    global cursor 

    conn= pyodbc.connect(os.getenv("Connection_String"))
    cursor= conn.cursor()


def GetUserByID(id):
    cursor.execute(f'SELECT * FROM [User] WHERE id = {id}')
    row= cursor.fetchone()
    data= str(row)

    return data