import os
import UI

from datetime import date, timedelta, datetime

async def RequestLeave(ctx, client, leavetype, startdate, enddate, leavesChannel):
    current_time = datetime.now().hour
    if ValidateDates(startdate, enddate):
        if CheckAvailableBalance(startdate, enddate, leavetype):
            if current_time >= 12:
                await UI.WarnRequester(ctx, client, startdate, enddate, leavesChannel)
            else:
                await UI.CompleteRequest(ctx, startdate, enddate, leavesChannel, leavetype)

        else:
            await ctx.send(content = UI.GetCaption(2) + str(int(os.getenv("Abdo_Annual_Leaves"))))

    else:
        await ctx.send(content = UI.GetCaption(3))

# helper functions
def CheckAvailableBalance(startdate: str, enddate: str, leavetype):
    requestedDays = GetRequestedDays(startdate, enddate)

    returnValues = {
        1: int(os.getenv("Abdo_Annual_Leaves")) - requestedDays,
        2: int(os.getenv("Abdo_Emergency_Leaves")) - requestedDays,
        3: int(os.getenv("Abdo_Sick_Leaves")) - requestedDays
    }

    return returnValues[leavetype] >= 0

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
