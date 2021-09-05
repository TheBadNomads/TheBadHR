import Utilities as utils

from db import db
from datetime import datetime

def GetLeaveByID(id):
    db.GetDBCursor().execute(f'SELECT * FROM [leaves] WHERE id = {id}')
    leave = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchone()]

    return leave

def GetLeaveByRequestID(request_id):
    db.GetDBCursor().execute(f'SELECT * FROM [leaves] WHERE request_id = {request_id}')
    leaves = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]

    return leaves

def InsertLeave(member_id:int, request_id:int, leave_type:int, leave_status:str, date:datetime, reason:str, remark:str):
    try:
        db.GetDBCursor().execute(
            "INSERT INTO [leaves] (member_id, request_id, leave_type, leave_status, date, reason, remark) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (member_id, request_id, leave_type, leave_status, date, reason, remark)
        )
        db.GetDBConnection().commit()
        return "Success"

    except Exception as e:
        db.GetDBConnection().rollback()
        return "Failed"