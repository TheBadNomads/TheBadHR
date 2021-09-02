import Utilities as utils

from db import db
from datetime import datetime

def GetLeaveByID(id):
    db.GetDBCursor().execute(f'SELECT * FROM [leaves] WHERE id = {id}')
    leave = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()][0]

    return leave

def GetLeavesByRequestID(request_id):
    db.GetDBCursor().execute(f'SELECT * FROM [leaves] WHERE request_id = {request_id}')
    leaves = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]

    return leaves

def GetLeaveStatus(request_id):
    db.GetDBCursor().execute(f'SELECT leave_status FROM [leaves] WHERE request_id = {request_id}')
    row = db.GetDBCursor().fetchone()
    leave = utils.ConvertJsonToDic(row)

    return leave["leave_status"]

def InsertLeave(member_id:int, request_id:int, leave_type:int, leave_status:str, date:datetime, reason:str, remark:str):
    try:
        db.GetDBCursor().execute(
            "INSERT INTO [leaves] (member_id, request_id, leave_type, date, reason, remark, leave_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (member_id, request_id, leave_type, date, reason, remark, leave_status)
        )
        db.GetDBConnection().commit()
        return "Success"

    except Exception as e:
        db.GetDBConnection().rollback()
        return "Failed"

def UpdateLeaveStatus(request_id, leave_status):
    try:
        db.GetDBCursor().execute("UPDATE [leaves] SET leave_status = ? WHERE request_id = ?", leave_status, request_id)
        db.GetDBConnection().commit()
        return "Success"

    except Exception as e:
        db.GetDBConnection().rollback()
        return "Failed"