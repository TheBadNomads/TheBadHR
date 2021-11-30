import Utilities as utils
import os

from db import db
from datetime import datetime
from Leave import leave_db

def GetMemberByID(id):
    db.GetDBCursor().execute(f'SELECT * FROM [members] WHERE id = {id}')
    member = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()][0]

    return member
    
def GetMembers():
    db.GetDBCursor().execute(f'SELECT * FROM [members]')
    members = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]

    return members

def InsertMember(id:int, name:str, email:str, start_date:datetime):
    try:
        db.GetDBCursor().execute(
            "INSERT INTO [members] (id, name, email, start_date) VALUES (?, ?, ?, ?)",
            (id, name, email, start_date)
        )    
        leave_db.InsertInitialLeaveBalance(id, start_date)
        db.GetDBConnection().commit()
        return "Success"

    except Exception as e:
        db.GetDBConnection().rollback()
        return "failed"

def CalculateProratedAnnualLeaves(member_id):
    start_month = GetMemberByID(member_id)["start_date"].month
    leaves_months_count = (12 - start_month) + 1
    starting_balance = int(os.getenv("Annual_Leaves_Max_Count"))
    leave_balance_per_month = starting_balance / 12
    return leaves_months_count * leave_balance_per_month
