import Utilities as utils
import datetime

from db import db

def GetLeaveByID(id):
    db.GetDBCursor().execute(f'SELECT * FROM [leaves] WHERE id = {id}')
    leave = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()][0]
    return leave

def GetLeavesMemberID(member_id):
    db.GetDBCursor().execute(f"SELECT * FROM [leaves] WHERE member_id = {member_id}")
    leaves = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]
    return leaves

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

def InsertLeave(member_id, request_id, leave_type, date, reason, remark, leave_status):
    if IsLeaveRequestedAfterCore(date):
        if GetLeaveBalance(member_id, "Emergency") > 0:
            leave_type = "Emergency"
        else:
            leave_type = "Unpaid"

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

def InsertInitialLeaveBalance(member_id:int, start_date:datetime):
    try:
        leave_types_with_balance = utils.CalculateInitialLeavesBalance(GetLeaveTypesWithBalance(), start_date)

        for name, balance in leave_types_with_balance.items():
            try:
                db.GetDBCursor().execute(
                    "INSERT INTO [leavesBalance] (member_id, leave_type, balance) VALUES (?, ?, ?)",
                    (member_id, name, balance)
                )
            except Exception as e:
                db.GetDBConnection().rollback()
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
    if IsLeaveRequest(message_id):
        return GetLeaveStatus(message_id).lower() == "pending"
    
    return False

def IsLeaveRequestedAfterCore(startdate):
    current_hour = datetime.datetime.now().time()
    end_of_core = datetime.time(13)
    today = datetime.datetime.today().date()

    if (startdate.date() == today):
        return True
    
    if ((current_hour >= end_of_core) and (startdate.date() == today + datetime.timedelta(1))):
        return True

    return  False     
