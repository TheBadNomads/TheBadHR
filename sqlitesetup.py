import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

connection = sqlite3.connect(os.getenv("DB_File"))

cursor = connection.cursor()

with open('SQLite_Setup.sql', 'r') as sql_file:
    sql_script = sql_file.read()
cursor.executescript(sql_script)

connection.commit()

connection.close()