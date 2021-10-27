import Utilities as utils

from db import db
from datetime import datetime
from Leave import leave_db

def GetMemberByID(id):
    db.GetDBCursor().execute(f'SELECT * FROM [members] WHERE id = {id}')
    member = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()][0]

    return member
    
def GetMembers():
    db.GetDBCursor().execute(f'SELECT * FROM [members]')
    members = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]

    return members

def InsertMember(id:int, name:str, email:str, start_date:datetime):
    try:
        db.GetDBCursor().execute(
            "INSERT INTO [members] (id, name, email, start_date) VALUES (?, ?, ?, ?)",
            (id, name, email, start_date)
        )    
        leave_db.InsertInitialLeaveBalance(id, start_date)
        db.GetDBConnection().commit()
        return "Success"

    except Exception as e:
        db.GetDBConnection().rollback()
        return "failed"
