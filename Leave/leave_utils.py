import os
import sys
sys.path.append(".")

from datetime import timedelta, datetime
from .leave_db import leave

def CheckAvailableBalance(member, startdate: str, enddate: str, leavetype):
    requested_days_count = len(GetRequestedDays(startdate, enddate))

    return (leave.GetLeaveBalance(member.id, leavetype) - requested_days_count) >= 0

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

def isLeaveRequest(message_id):
    return len(leave.GetLeaveByRequestID(message_id)) != 0

def isPending(message_id):
    return leave.GetLeaveStatus(message_id) == "pending"