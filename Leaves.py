import os
import UI
import db

from datetime import date, timedelta, datetime

async def RequestLeave(ctx, client, leavetype, startdate, enddate, leavesChannel):
    current_time = datetime.now().hour
    if ValidateDates(startdate, enddate):
        if CheckAvailableBalance(ctx.author, startdate, enddate, leavetype):
            if current_time > 12:
                await UI.WarnRequester(ctx, client, startdate, enddate, leavesChannel, GetRequestedDays(startdate, enddate))
            else:
                await UI.CompleteRequest(ctx, startdate, enddate, leavesChannel, leavetype, GetRequestedDays(startdate, enddate))

        else:
            await ctx.send(content = UI.GetCaption(2) + str(db.GetLeaveBalance(ctx.author.id, leavetype)))

    else:
        await ctx.send(content = UI.GetCaption(3))

# helper functions
def CheckAvailableBalance(user, startdate: str, enddate: str, leavetype):
    requestedDays = GetRequestedDays(startdate, enddate)

    return (db.GetLeaveBalance(user.id, leavetype) - requestedDays) >= 0

def GetRequestedDays(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    total_days = []

    for i in range((eDate - sDate).days + 1):
        day = sDate + timedelta(days=i)
        if day.weekday() != 4 and day.weekday() != 5:
            total_days.append(day) 

    return len(total_days)

def ValidateDates(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    return eDate >= sDate
