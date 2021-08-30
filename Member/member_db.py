import Utilities as utils

from db import db
from datetime import datetime

def GetMemberByID(id):
    db.GetDBCursor().execute(f'SELECT * FROM [members] WHERE id = {id}')
    row = db.GetDBCursor().fetchone()
    member = utils.ConvertJsonToDic(row)

    return member
    
def GetMembers():
    db.GetDBCursor().execute(f'SELECT * FROM [members]')
    rows = db.GetDBCursor().fetchall()
    members = map(utils.ConvertJsonToDic, rows)

    return members

def InsertMember(id:int, name:str, email:str, start_date:datetime):
    try:
        db.GetDBCursor().execute(
            "INSERT INTO [members] (id, name, email, start_date, leave_date) VALUES (?, ?, ?, ?, ?)",
            (id, name, email, datetime.strptime(start_date, '%m/%d/%Y'), None)
        )    
        db.GetDBConnection().commit()
        # TODO: Insert Leave balance on success

        return "Success"

    except Exception as e:
        db.GetDBConnection().rollback()

        return "failed"