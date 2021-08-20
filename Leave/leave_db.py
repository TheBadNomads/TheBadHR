import leave_utils as lu

from db import db
from datetime import datetime
from leave_type_db import LeaveType

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

    def GetLeaveByID(id):
        db.GetDBCursor().execute(f'SELECT * FROM [leaves] WHERE id = {id}')
        row = db.GetDBCursor().fetchone()

        return leave(row)

    def GetLeaveByRequestID(request_id):
        db.GetDBCursor().execute(f'SELECT * FROM [leaves] WHERE request_id = {request_id}')
        rows = db.GetDBCursor().fetchall()
        leaves = []
        for row in rows:
            leaves.append(leave(row))

        return leaves

    def GetLeaveStatus(request_id):
        db.GetDBCursor().execute(f'SELECT leave_status FROM [leaves] WHERE request_id = {request_id}')
        row = db.GetDBCursor().fetchone()

        return str(row[0])

    def GetLeaveBalance(member_id, leave_type):
        db.GetDBCursor().execute(f'SELECT balance FROM [leavesBalance] WHERE member_id = {member_id} AND leave_type = {leave_type}')
        row = db.GetDBCursor().fetchone()

        return float(row[0])
    

    def InsertLeave(member_id:int, request_id:int, leave_type:int, leave_status:str, date:datetime, reason:str, remark:str):
        success = True
        try:
            db.GetDBCursor().execute(
                "INSERT INTO [leaves] (member_id, request_id, leave_type, leave_status, date, reason, remark) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (member_id, request_id, leave_type, leave_status, date, reason, remark)
            )
            db.GetDBConnection().commit()

        except Exception as e:
            db.GetDBConnection().rollback()
            success = False

        return success

    def InsertLeaveBalance(member_id:int, start_date:datetime):
        success = True
        try:
            for leaveType in LeaveType.GetLeaveTypes():
                try:
                    db.GetDBCursor().execute(
                        "INSERT INTO [leavesBalance] (member_id, leave_type, balance) VALUES (?, ?, ?)",
                        (member_id, leaveType.id, lu.CalculateLeaveTypeBalance(leaveType.id, start_date))
                    )
                except Exception as e:
                    print(e)
                    success = False

            db.GetDBConnection().commit()

        except Exception as e:
            db.GetDBConnection().rollback()
            success = False

        return success
    
    
    def UpdateLeaveStatus(request_id, leave_status):
        success = True
        try:
            db.GetDBCursor().execute("UPDATE [leaves] SET leave_status = ? WHERE request_id = ?", leave_status, request_id)
            db.GetDBConnection().commit()

        except Exception as e:
            db.GetDBConnection().rollback()
            success = False

        return success
    
    def UpdateLeaveBalance(member_id, leave_type, requested_days):
        success = True
        try:
           db.GetDBCursor().execute("UPDATE [leavesBalance] SET balance = balance + ? WHERE member_id = ? AND leave_type = ?", requested_days, member_id, leave_type)
           db.GetDBConnection().commit()

        except Exception as e:
            db.GetDBConnection().rollback()
            success = False

        return success
