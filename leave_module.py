import db
from datetime import datetime

class leave:
    def __init__(self, attrs):
        self.id = attrs[0]
        self.member_id = attrs[1]
        self.request_id = attrs[2]
        self.leave_type = attrs[3]
        self.leave_status = attrs[4]
        self.date = attrs[5]
        self.reason = attrs[6]
        self.remark = attrs[7]

# GET
def GetLeaveByID(id):
    db.cursor.execute(f'SELECT * FROM [leaves] WHERE id = {id}')
    row = db.cursor.fetchone()

    return leave(row)

def GetLeaveByRequestID(request_id):
    db.cursor.execute(f'SELECT * FROM [leaves] WHERE request_id = {request_id}')
    row = db.cursor.fetchone()

    return leave(row)

def GetLeaveStatus(request_id):
    db.cursor.execute(f'SELECT leave_status FROM [leaves] WHERE request_id = {request_id}')
    row = db.cursor.fetchone()

    return str(row[0])

def GetLeaveBalance(member_id, leave_type):

    db.cursor.execute(f'SELECT balance FROM [leavesBalance] WHERE member_id = {member_id} AND leave_type = {leave_type}')
    row = db.cursor.fetchone()

    return float(row[0])

# POST
def InsertLeave(member_id:int, request_id:int, leave_type:int, leave_status:str, date:datetime, reason:str, remark:str):
    error = False
    try:
        db.cursor.execute(
            "INSERT INTO [leaves] (member_id, request_id, leave_type, leave_status, date, reason, remark) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (member_id, request_id, leave_type, leave_status, date, reason, remark)
        )
    except Exception as e:
        print(e)
        error = True

    if not error:
        db.conn.commit()
    else:
        db.conn.rollback()

    return error

# PUT
def UpdateLeaveStatus(request_id, leave_status):
    error= False
    try:
        db.cursor.execute("UPDATE [leaves] SET leave_status = ? WHERE request_id = ?", leave_status, request_id)
    except Exception as e:
        print(e)
        error = True

    if not error:
        db.conn.commit()
    else:
        db.conn.rollback()

    return error

def UpdateLeaveBalance(member_id, leave_type, requested_days):
    error = False
    try:
        db.cursor.execute("UPDATE [leavesBalance] SET balance = balance + ? WHERE member_id = ? AND leave_type = ?", requested_days, member_id, leave_type) 
    except Exception as e:
        print(e)
        error = True

    if not error:
        db.conn.commit()
    else:
        db.conn.rollback()

    return error