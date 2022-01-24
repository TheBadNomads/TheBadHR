import os
from dotenv import load_dotenv

load_dotenv()

if(not os.path.exists("./" + os.getenv("DB_File"))):
    import sqlitesetup
    print("Database Created")
print("Initialization Complete!")
