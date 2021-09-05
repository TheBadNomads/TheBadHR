import Utilities as utils

from db import db
from datetime import datetime

def GetMemberByID(id):
    db.GetDBCursor().execute(f'SELECT * FROM [members] WHERE id = {id}')
    member = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchone()]

    return member
    
def GetMembers():
    db.GetDBCursor().execute(f'SELECT * FROM [members]')
    members = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]

    return members

def InsertMember(id:int, name:str, email:str, start_date:datetime):
    try:
        db.GetDBCursor().execute(
            "INSERT INTO [members] (id, name, email, start_date) VALUES (?, ?, ?, ?)",
            (id, name, email, datetime.strptime(start_date, '%m/%d/%Y'))
        )    
        db.GetDBConnection().commit()
        # TODO: Insert Leave balance on success

        return "Success"

    except Exception as e:
        db.GetDBConnection().rollback()

        return "failed"