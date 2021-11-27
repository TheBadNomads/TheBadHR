import discord
import os
import datetime
import re 

def isNotBot(member):
    return not member.bot


def CalculateInitialLeavesBalance(leave_types, start_date):
    calculated_leave_types_balance = {}
    for leave_type in leave_types:
        calculated_leave_types_balance[leave_type["name"]] = CalculateProrataForLeave(leave_type["name"], start_date)
    return calculated_leave_types_balance

def CalculateProrataForLeave(leave_type, start_date):
    if leave_type == "Annual":
        return CalculateProratedAnnualLeaves(start_date, int(os.getenv("Annual_Leaves_Max_Count")))

    else:
        return float('inf')

def CalculateProratedAnnualLeaves(start_date, starting_balance):
    start_month = start_date.month
    leaves_months_count = (12 - start_month) + 1
    leave_balance_per_month = starting_balance / 12
    return leaves_months_count * leave_balance_per_month

def HasEnoughBalance(startdate, enddate, current_balance):
    requested_days_count = len(GetWorkDays(startdate, enddate))
    return current_balance >= requested_days_count

def GetWorkDays(startdate, enddate):
    work_days = []
    for i in range((enddate - startdate).days + 1):
        day = startdate + datetime.timedelta(days = i)
        if (day.weekday() not in [4, 5]):
            work_days.append(day) 
    return work_days
    
def IsAdmin(member):
    role = discord.utils.get(member.guild.roles, id = int(os.getenv("Admin_Role_id")))
    return (role in member.roles)

def GetMemberIDFromEmbed(embed):
    text = embed.description
    return int(re.match(r'<@!?(\d+)>', text).group(1))

def IsLateToApplyForLeave(leave_date):
    current_hour = datetime.datetime.now().time()
    end_of_core = datetime.time(13)
    today = datetime.datetime.today().date()

    if (leave_date.date() == today):
        return True
    
    if ((current_hour >= end_of_core) and (leave_date.date() == today + datetime.timedelta(1))):
        return True

    return  False 

def ConvertDatesToStrings(dates_array):
    return [day.strftime('%d/%m/%Y') for day in dates_array]

def FilterOutLeavesByStatus(leaves_array, leave_status):
    filtered_leaves = []
    for leave in leaves_array:
        if (leave["leave_status"].lower() != leave_status):
            filtered_leaves.append(leave)
    return filtered_leaves

def IsEmergencyLeave(leave_date, leave_type):
    return (IsLateToApplyForLeave(leave_date) and (leave_type.lower() == "annual"))

def IsUnpaidLeave(leave_balance, is_emergency, remaining_emergency_count):
    return ((leave_balance < 1) or ((is_emergency) and (remaining_emergency_count < 1)))

def GetDatesOfLeaves(leaves_array):
    return ([d['date'] for d in leaves_array])
