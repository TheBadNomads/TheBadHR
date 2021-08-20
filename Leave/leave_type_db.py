from db import db

class LeaveType:
    def __init__(self, attrs):
        self.id = attrs[0]
        self.name = attrs[1]

    def GetLeaveTypes():
        db.GetDBCursor().execute('SELECT * FROM [leaveTypes]')
        rows = db.GetDBCursor().fetchall()
        leave_types = []
        for row in rows:
                leave_types.append(LeaveType(row))

        return leave_types