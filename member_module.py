import db
from datetime import datetime

class member:
    def __init__(self, attrs):
        self.id = attrs[0]
        self.name = attrs[1]
        self.email = attrs[2]
        self.start_date = attrs[3]
        self.leave_date = attrs[4]
        self.position = attrs[5]

# GET
def GetMemeberByID(id):
    db.cursor.execute(f'SELECT * FROM [members] WHERE id = {id}')
    row = db.cursor.fetchone()
    
    return member(row)

# POST
def InsertUser(id:int, name:str, email:str, start_date:datetime, leave_date:datetime, position:int):
    error = False
    try:
        db.cursor.execute(
            "INSERT INTO [members] (id, name, email, start_date, leave_date, position) VALUES (?, ?, ?, ?, ?, ?)",
            (id, name, email, start_date, leave_date, position)
        )    
    except Exception as e:
        print(e)
        error = True

    if not error:
        db.conn.commit()
    else:
        db.conn.rollback()
    
    return error