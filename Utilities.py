from datetime import datetime

def isNotBot(member):
    return not member.bot

def CalculateInitialLeaveBalance(leave_type, start_date):
    # can be changed later to be retrived from DB
    leave_types = {
        "Annual": CalculateProratedAnnualLeaves(start_date),
        "Emergency": 5,
        "Sick": 365,
        "Unpaid": 365
    }

    return leave_types[leave_type]

def CalculateProratedAnnualLeaves(start_date):
    start_month = int(datetime.strftime(start_date,"%m"))
    leaves_months_count = (12 - start_month) + 1
    leave_balance_per_month = 21/12

    return leaves_months_count * leave_balance_per_month