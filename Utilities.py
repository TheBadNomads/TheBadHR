from datetime import datetime

def isNotBot(member):
    return not member.bot

def CalculateLeaveTypeBalance(leave_type, start_date):
    # can be changed later to be retrived from DB
    leave_types = {
        1: CalculateAnnual(start_date),
        2: 5,
        3: 365,
        4: 365
    }

    return leave_types[leave_type]

def CalculateAnnual(start_date):
    start_month = int(datetime.strftime(start_date,"%m"))
    leaves_months_count = (12 - start_month) + 1
    leave_balance_per_month = 21/12

    return leaves_months_count * leave_balance_per_month