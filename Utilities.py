import discord
import os
import datetime
import re
from calendar import monthrange

from Member import member_db

def isNotBot(member):
    return not member.bot

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

def IsUnpaidLeave(leave_type, leave_balance, is_emergency, remaining_emergency_count):
    if leave_type == "Sick":
        return False
        
    return ((leave_balance < 1) or ((is_emergency) and (remaining_emergency_count < 1)))

def GetDatesOfLeaves(leaves_array):
    return ([d['date'] for d in leaves_array])

def GetFieldFromEmbed(embed, field_name):
    embed_dict = embed.to_dict()
    for field in embed_dict["fields"]:
        if field["name"].lower() == field_name.lower():
            return field["value"]

def CalculatePercentage(numerator, denominator):
    return "{:.2f}".format((numerator / denominator) * 100)

def GetMembersFromMention(mention_string):
    members_list = []
    members_ids = re.findall(r'<@!?(\d+)>', mention_string)
    for member_id in members_ids:
        member = member_db.GetMemberByID(int(member_id))
        if member != None:
            members_list.append(member)
    return members_list

def GetMonthDaysCount(month, year):
    return monthrange(year, month)[1]
