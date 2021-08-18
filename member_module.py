import db
import leave_module as lm

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

def GetPositions():
    db.cursor.execute('SELECT * FROM [positions]')
    rows = db.cursor.fetchall()

    return rows

# POST
def InsertMember(id:int, name:str, email:str, start_date:datetime, leave_date:datetime, position:int):
    success = True
    try:
        db.cursor.execute(
            "INSERT INTO [members] (id, name, email, start_date, leave_date, position) VALUES (?, ?, ?, ?, ?, ?)",
            (id, name, email, start_date, leave_date, position)
        )    
    except Exception as e:
        print(e)
        success = False

    leaves_success = lm.InsertLeaveBalance(id, start_date)

    if success and leaves_success:
        db.conn.commit()
    else:
        db.conn.rollback()
    
    return success
