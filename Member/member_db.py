import os
import datetime

from db import db

def GetMemberByID(id):
    db.execute(f'SELECT * FROM [members] WHERE id = {id}')
    member = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()][0]

    return member
    
def GetMembers():
    db.execute(f'SELECT * FROM [members]')
    members = [dict(zip([column[0] for column in db.GetDBCursor().description], row)) for row in db.GetDBCursor().fetchall()]

    return members

def InsertMember(id:int, name:str, email:str, start_date:datetime):
    db.execute(
        "INSERT INTO [members] (id, name, email, start_date) VALUES (?, ?, ?, ?)",
        (id, name, email, start_date)
    )

def CalculateProratedAnnualLeaves(member_id):
    start_date = GetMemberByID(member_id)["start_date"]
    start_year = start_date.year
    if datetime.date.today().year > start_year :
        return int(os.getenv("Annual_Leaves_Max_Count"))
        
    start_month = start_date.month
    leaves_months_count = (12 - start_month) + 1
    starting_balance = int(os.getenv("Annual_Leaves_Max_Count"))
    leave_balance_per_month = starting_balance / 12
    return leaves_months_count * leave_balance_per_month
