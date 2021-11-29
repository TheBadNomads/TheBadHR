import Utilities as utils
import datetime
import os

from db import db
from Member import member_db

def GetLeaveByID(id):
    db.GetDBCursor().execute(f'SELECT * FROM [leaves] WHERE id = {id}')
    leave = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()][0]
    return leave

def GetLeavesByMemberID(member_id):
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

def GetEmergencyLeavesForYear(member_id, year):
    db.GetDBCursor().execute(f"SELECT * FROM [leaves] WHERE member_id = {member_id} AND is_emergency = 'True' AND YEAR(date) = {year}")
    leaves = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]
    return leaves

def GetAnnualLeaveBalance(member_id):
    start_date = member_db.GetMemberByID(member_id)["start_date"]
    initial_balance = utils.CalculateProratedAnnualLeaves(start_date, int(os.getenv("Annual_Leaves_Max_Count")))
    extra_balance = GetExtraBalance(member_id, "Annual")
    used_balance = len(list(filter(lambda leave: leave['leave_type'] == 'Annual', GetLeavesByMemberID(member_id))))
    current_balance = (initial_balance + extra_balance) - used_balance
    return current_balance

def GetExtraBalance(member_id, leave_type):
    db.GetDBCursor().execute(f"SELECT SUM(days_count) FROM extraBalance WHERE recipient_id = {member_id} AND leave_type = '{leave_type}'")
    return db.GetDBCursor().fetchone()[0] or 0 

def GetLeaveTypes():
    db.GetDBCursor().execute('SELECT * FROM [leaveTypes]')
    leaves_types = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]
    return leaves_types

def InsertLeave(member_id, request_id, leave_type, date, reason, remark, leave_status, is_emergency, is_unpaid):
    try:
        db.GetDBCursor().execute(
            "INSERT INTO [leaves] (member_id, request_id, leave_type, date, reason, remark, leave_status, is_emergency, is_unpaid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (member_id, request_id, leave_type, date, reason, remark, leave_status, is_emergency, is_unpaid)
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

def IsLeaveRequest(message_id):
    return len(GetLeavesByRequestID(message_id)) != 0

def IsLeaveRequestPending(message_id):
    if IsLeaveRequest(message_id):
        return GetLeaveStatus(message_id).lower() == "pending"
    
    return False    
