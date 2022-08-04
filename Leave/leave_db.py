import datetime
import os

from db import db
from dateutil.relativedelta import relativedelta
from Member import member_db

def GetLeaveByID(id):
    db.execute(f'SELECT * FROM [leaves] WHERE id = {id}')
    leave = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()][0]
    return leave

def GetLeavesByMemberID(member_id):
    db.execute(f"SELECT * FROM [leaves] WHERE member_id = {member_id}")
    leaves = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]
    return leaves

def GetLeavesBetween(start_date, end_date, member):
    query = f"SELECT * FROM [leaves] WHERE date >= '{start_date}' AND date <= '{end_date}'"
    if (member != None):
        query += f' AND member_id = {member.id}'
    db.execute(query)
    leaves = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]
    return leaves

def GetLeavesByRequestID(request_id):
    db.execute(f'SELECT * FROM [leaves] WHERE request_id = {request_id}')
    leaves = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]
    return leaves

def GetLeaveStatus(request_id):
    db.execute(f'SELECT leave_status FROM [leaves] WHERE request_id = {request_id}')
    leave = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()][0]
    return leave["leave_status"]

def GetApprovedPaidLeaves(member_id, start_date, end_date):
    query = f"SELECT * FROM [leaves] WHERE member_id = {member_id} AND leave_status = 'Approved' AND is_unpaid = 'False' AND date >= '{start_date}' AND date <= '{end_date}'"
    db.execute(query)
    leaves = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]
    return leaves

def GetApprovedEmergencyLeaves(member_id, start_date, end_date):
    query = f"SELECT * FROM [leaves] WHERE member_id = {member_id} AND leave_status = 'Approved' AND is_emergency = 'True' AND date >= '{start_date}' AND date <= '{end_date}'"
    db.execute(query)
    leaves = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]
    return leaves

def GetApprovedUnpaidLeaves(member_id, start_date, end_date):
    query = f"SELECT * FROM [leaves] WHERE member_id = {member_id} AND leave_status = 'Approved' AND is_unpaid = 'True' AND date >= '{start_date}' AND date <= '{end_date}'"
    db.execute(query)
    leaves = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]
    return leaves

def GetApprovedSickLeaves(member_id, start_date, end_date):
    query = f"SELECT * FROM [leaves] WHERE member_id = {member_id} AND leave_status = 'Approved' AND leave_type = 'Sick' AND date >= '{start_date}' AND date <= '{end_date}'"
    db.execute(query)
    leaves = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]
    return leaves

def GetAnnualLeaveBalance(member_id):
    initial_balance = member_db.CalculateProratedAnnualLeaves(member_id)
    extra_balance = GetExtraBalance(member_id, "Annual")
    start_date = datetime.datetime(datetime.date.today().year - 1, int(os.getenv("End_of_Year_Report_Month")), int(os.getenv("End_of_Year_Report_Day")))
    end_date = start_date + relativedelta(years = 1)
    used_balance = len(list(filter(lambda leave: leave['leave_type'] == 'Annual', GetApprovedPaidLeaves(member_id, start_date, end_date))))
    current_balance = initial_balance + extra_balance - used_balance
    return current_balance

def GetExtraBalance(member_id, leave_type):
    db.execute(f"SELECT SUM(days_count) FROM extraBalance WHERE recipient_id = {member_id} AND leave_type = '{leave_type}' AND strftime('%Y', date) = {datetime.date.today().year}")
    return db.GetDBCursor().fetchone()[0] or 0 

def GetLeaveTypes():
    db.execute('SELECT * FROM [leaveTypes]')
    leaves_types = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]
    return leaves_types

def InsertLeave(member_id, request_id, leave_type, date, reason, remark, leave_status, is_emergency, is_unpaid):
    db.execute(
        "INSERT INTO [leaves] (member_id, request_id, leave_type, date, reason, remark, leave_status, is_emergency, is_unpaid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (member_id, request_id, leave_type, date, reason, remark, leave_status, is_emergency, is_unpaid)
    )

def InsertExtraBalance(date, creditor_id, recipient_id, leave_type, reason, days_count):
    db.execute(
        "INSERT INTO [extraBalance] (date, creditor_id, recipient_id, leave_type, reason, days_count) VALUES (?, ?, ?, ?, ?, ?)",
        (date, creditor_id, recipient_id, leave_type, reason, days_count)
    )

def UpdateLeaveStatus(request_id, leave_status):
    db.execute("UPDATE [leaves] SET leave_status = ? WHERE request_id = ?", (leave_status, request_id))

def IsLeaveRequest(message_id):
    return len(GetLeavesByRequestID(message_id)) != 0

def IsLeaveRequestPending(message_id):
    if IsLeaveRequest(message_id):
        return GetLeaveStatus(message_id).lower() == "pending"
    
    return False

def GetRemainingEmergencyLeavesCount(member_id):
    start_date = datetime.datetime(datetime.date.today().year, 1, 1)
    end_date = datetime.datetime(datetime.date.today().year + 1, 1, 1)
    requested_emergency_count = len(GetApprovedEmergencyLeaves(member_id, start_date, end_date))
    max_emergency_count = int(os.getenv("Emergency_Leaves_Max_Count"))
    return (max_emergency_count - requested_emergency_count)
