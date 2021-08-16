import pyodbc 
import os

def load_db():
    global conn 
    global cursor 

    conn = pyodbc.connect(os.getenv("Connection_String"))
    cursor = conn.cursor()