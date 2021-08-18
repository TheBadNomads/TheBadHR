import db
import UI

from datetime import timedelta, datetime

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
    rows = db.cursor.fetchall()
    leaves = []
    for row in rows:
        leaves.append(leave(row))

    return leaves

def GetLeaveStatus(request_id):
    db.cursor.execute(f'SELECT leave_status FROM [leaves] WHERE request_id = {request_id}')
    row = db.cursor.fetchone()

    return str(row[0])

def GetLeaveBalance(member_id, leave_type):

    db.cursor.execute(f'SELECT balance FROM [leavesBalance] WHERE member_id = {member_id} AND leave_type = {leave_type}')
    row = db.cursor.fetchone()

    return float(row[0])

def GetLeaveTypes():
    db.cursor.execute('SELECT * FROM [leaveTypes]')
    rows = db.cursor.fetchall()

    return rows

# POST
def InsertLeave(member_id:int, request_id:int, leave_type:int, leave_status:str, date:datetime, reason:str, remark:str):
    success = True
    try:
        db.cursor.execute(
            "INSERT INTO [leaves] (member_id, request_id, leave_type, leave_status, date, reason, remark) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (member_id, request_id, leave_type, leave_status, date, reason, remark)
        )
    except Exception as e:
        print(e)
        success = False

    if success:
        db.conn.commit()
    else:
        db.conn.rollback()

    return success

def InsertLeaveBalance(member_id:int, start_date:datetime):
    success = True
    for type in GetLeaveTypes():
        try:
            db.cursor.execute(
                "INSERT INTO [leavesBalance] (member_id, leave_type, balance) VALUES (?, ?, ?)",
                (member_id, type[0], CalculateLeaveTypeBalance(type[0], start_date))
            )
        except Exception as e:
            print(e)
            success = False

    if success:
        db.conn.commit()
    else:
        db.conn.rollback()

    return success

# PUT
def UpdateLeaveStatus(request_id, leave_status):
    success = True
    try:
        db.cursor.execute("UPDATE [leaves] SET leave_status = ? WHERE request_id = ?", leave_status, request_id)
    except Exception as e:
        print(e)
        success = False

    if success:
        db.conn.commit()
    else:
        db.conn.rollback()

    return success

def UpdateLeaveBalance(member_id, leave_type, requested_days):
    success = True
    try:
        db.cursor.execute("UPDATE [leavesBalance] SET balance = balance + ? WHERE member_id = ? AND leave_type = ?", requested_days, member_id, leave_type) 
    except Exception as e:
        print(e)
        success = False

    if success:
        db.conn.commit()
    else:
        db.conn.rollback()

    return success

# HELPER FUNCTIONS
def CheckAvailableBalance(member, startdate: str, enddate: str, leavetype):
    requested_days_count = len(GetRequestedDays(startdate, enddate))

    return (GetLeaveBalance(member.id, leavetype) - requested_days_count) >= 0

def GetRequestedDays(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    total_days = []

    for i in range((eDate - sDate).days + 1):
        day = sDate + timedelta(days=i)
        if day.weekday() != 4 and day.weekday() != 5:
            total_days.append(day) 

    return total_days

def ValidateDates(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    return eDate >= sDate

def CalculateLeaveTypeBalance(leave_type, start_date):
    # can be changed later to be retrived from DB
    leave_types = {
        1: 21,
        2: 5,
        3: 365
    }

    start_month = int(start_date.strftime("%m"))
    leaves_months_count = (12 - start_month) + 1
    leave_balance_per_month = leave_types[leave_type]/12

    return leaves_months_count * leave_balance_per_month

# COMMANDS
async def RequestLeave(ctx, client, leavetype, startdate, enddate, leavesChannel, reason):
    current_time = datetime.now().hour
    if ValidateDates(startdate, enddate):
        if CheckAvailableBalance(ctx.author, startdate, enddate, leavetype):
            if current_time > 12:
                await UI.WarnRequester(ctx, client, startdate, enddate, leavesChannel, reason)
            else:
                await UI.CompleteRequest(ctx, startdate, enddate, leavesChannel, leavetype, reason)

        else:
            await ctx.send(content = UI.GetCaption(2) + str(GetLeaveBalance(ctx.author.id, leavetype)))

    else:
        await ctx.send(content = UI.GetCaption(3))