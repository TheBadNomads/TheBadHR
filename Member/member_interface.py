import sys
sys.path.append(".")

from .member_db import member
from datetime import datetime

def InsertMember(id, name, email, start_date):
    return member.InsertMember(id, name, email, datetime.strptime(start_date, '%m/%d/%Y'), datetime.strptime('1/1/3000', '%m/%d/%Y'))

def GetMemberByID(id):
    return member.GetMemeberByID(id)

def GetMembers():
    return member.GetMemebers()