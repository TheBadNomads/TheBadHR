import sys
sys.path.append(".")

from .member_db import member
from .position_db import position
from datetime import datetime

def InsertMember(id, name, email, start_date, leave_date, position):
    return member.InsertMember(id, name, email, datetime.strptime(start_date, '%m/%d/%Y'), datetime.strptime(leave_date, '%m/%d/%Y'), position)

def GetMemberByID(id):
    return member.GetMemeberByID(id)

def GetMembers():
    return member.GetMemebers()

def GetPositions():
    return position.GetPositions()