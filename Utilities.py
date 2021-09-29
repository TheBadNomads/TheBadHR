from datetime import datetime, timedelta

def isNotBot(member):
    return not member.bot


def CalculateInitialLeavesBalance(leave_types_with_balance, start_date):
    calculated_leave_types_balance = {}
    for leave_type in leave_types_with_balance:
        calculated_leave_types_balance[leave_type["name"]] = CalculateProrataForLeave(leave_type["name"], start_date, leave_type["starting_balance"])
    
    return calculated_leave_types_balance

def CalculateProrataForLeave(leave_type, start_date, starting_balance):
    if leave_type == "Annual":
        return CalculateProratedAnnualLeaves(start_date, starting_balance)

    else:
        return starting_balance

def CalculateProratedAnnualLeaves(start_date, starting_balance):
    start_month = int(datetime.strftime(start_date,"%m"))
    leaves_months_count = (12 - start_month) + 1
    leave_balance_per_month = starting_balance/12

    return leaves_months_count * leave_balance_per_month

def HasEnoughBalance(startdate: str, enddate: str, current_balance):
    requested_days_count = len(GetRequestedDays(startdate, enddate))
    return current_balance >= requested_days_count

def GetRequestedDays(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')
    requested_days = []
    for i in range((eDate - sDate).days + 1):
        day = sDate + timedelta(days = i)
        if (day.weekday() not in [4, 5]):
            requested_days.append(day) 

    return requested_days

def ValidateDates(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    return eDate >= sDate