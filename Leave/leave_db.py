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
    leave = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()][0]

    return leave["leave_status"]

def GetLeaveBalance(member_id, leave_type):
    db.GetDBCursor().execute(f"SELECT balance FROM [leavesBalance] WHERE member_id = {member_id} AND leave_type = '{leave_type}'")
    leaves_balance = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()][0]

    return float(leaves_balance["balance"])

def GetLeaveTypesWithBalance():
    db.GetDBCursor().execute('SELECT * FROM [leaveTypesWithBalance]')
    leaves_types = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]

    return leaves_types

def InsertLeave(member_id:int, request_id:int, leave_type:int, date:datetime, reason:str, remark:str, leave_status:str):
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

def InsertLeaveBalance(member_id:int, start_date:datetime):
    try:
        leave_types_with_balance = utils.CalculateInitialLeavesBalance(GetLeaveTypesWithBalance(), start_date)

        for name, balance in leave_types_with_balance:
            try:
                db.GetDBCursor().execute(
                    "INSERT INTO [leavesBalance] (member_id, leave_type, balance) VALUES (?, ?, ?)",
                    (member_id, name, balance)
                )
            except Exception as e:
                print(e)
                return "Failed"

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

def UpdateLeaveBalance(member_id, leave_type, requested_days):
    try:
        db.GetDBCursor().execute("UPDATE [leavesBalance] SET balance = balance + ? WHERE member_id = ? AND leave_type = ?", requested_days, member_id, leave_type)
        db.GetDBConnection().commit()
        return "Success"

    except Exception as e:
        db.GetDBConnection().rollback()
        return "Failed"

def IsLeaveRequest(message_id):
    return len(GetLeavesByRequestID(message_id)) != 0

def IsLeaveRequestPending(message_id):
    return GetLeaveStatus(message_id).lower() == "pending"