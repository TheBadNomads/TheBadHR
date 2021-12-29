import datetime
import Utilities as utils
import os
import UI
import collections

from Channels import Channels
from db import db
from Leave import leave_db

async def ProcessLeaveRequest(ctx, member, client, leave_type, start_date, end_date, reason):
    is_request_valid, message = IsLeaveRequestValid(member.id, start_date, end_date)
    if is_request_valid:
        return await SubmitRequest(ctx, member, client, start_date, end_date, leave_type, reason)   
        
    else:
        return message

async def SubmitRequest(ctx, member, client, start_date, end_date, leave_type, reason):
    message_id = await SendLeaveRequestToChannel(ctx, client, start_date, end_date, leave_type, reason)
    return AddLeaveRequestToDB(member, message_id, start_date, end_date, leave_type, "Pending", reason)
    
async def SendLeaveRequestToChannel(ctx, client, start_date, end_date, leave_type, reason):
    embed = UI.CreateLeaveEmbed(ctx, start_date, end_date, leave_type, reason)
    channel = Channels.GetLeaveApprovalsChannel(client)
    message = await channel.send(embed = embed)
    await AddEmojisToLeaveMessage(message)
    return message.id

def AddLeaveRequestToDB(member, message_id, start_date, end_date, leave_type, leave_status, reason):
    if message_id == None:
        return ("Failed")

    try:
        work_days = utils.GetWorkDays(start_date, end_date)
        remaining_emergency_count = GetRemainingEmergencyLeavesCount(member.id)
        annual_leave_balance = leave_db.GetAnnualLeaveBalance(member.id)
        for day in work_days:
            is_emergency = utils.IsEmergencyLeave(day, leave_type)
            is_unpaid = utils.IsUnpaidLeave(leave_type, annual_leave_balance, is_emergency, remaining_emergency_count)
            if ((leave_type == "Annual") and not (is_unpaid)):
                annual_leave_balance -= 1
            leave_db.InsertLeave(member.id, message_id, leave_type, day, reason, "", leave_status, is_emergency, is_unpaid)
        return (db.GetCaption(1))
        
    except Exception as e:
        print(e)
        return ("Failed")
                
async def HandleLeaveReactions(client, payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    embed = message.embeds[0]
    
    action = UI.ParseEmoji(payload.emoji)
    if action == None:
        return

    if payload.member.bot:
        return
    
    if not (utils.IsAdmin(payload.member)):
        return
        
    if action == "Reverted":
        if not (leave_db.IsLeaveRequestPending(payload.message_id)):
            leave_db.UpdateLeaveStatus(payload.message_id, "Pending")
            await UI.UpdateLeaveEmbed(payload.member, message, embed, "Pending")
            await InformMemberAboutLeaveStatus(client, embed, payload.member, action)
            await message.clear_reactions()
            await AddEmojisToLeaveMessage(message)
    elif leave_db.IsLeaveRequestPending(payload.message_id):
        try:
            leave_db.UpdateLeaveStatus(payload.message_id, action)
            await UI.UpdateLeaveEmbed(payload.member, message, embed, action)
            await InformMemberAboutLeaveStatus(client, embed, payload.member, action)
        except Exception as e:
            print(e)

async def InformMemberAboutLeaveStatus(client, embed, admin, status):
    member = await client.fetch_user(utils.GetMemberIDFromEmbed(embed))

    reason = utils.GetFieldFromEmbed(embed, "reason")
    leave_type = utils.GetFieldFromEmbed(embed, "leave type")
    start_date = utils.GetFieldFromEmbed(embed, "start date")
    end_date = utils.GetFieldFromEmbed(embed, "end date")

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    reply_embed = UI.CreateInformMemberOfLeaveStatusEmbed(status, admin.display_name, reason, leave_type, start_date, end_date)
    await member.send(embed = reply_embed)

def GetRequestedLeavesBetween(member_id, start_date, end_date):
    work_days = utils.GetWorkDays(start_date, end_date)
    previous_leaves = leave_db.GetLeavesByMemberID(member_id)
    requested_leaves = []
    for leave in previous_leaves:
        if (leave["date"] in work_days):
           requested_leaves.append(leave)
    return requested_leaves

def GetRemainingEmergencyLeavesCount(member_id):
    requested_emergency_count = len(leave_db.GetEmergencyLeavesForYear(member_id, datetime.date.today().year))
    max_emergency_count = int(os.getenv("Emergency_Leaves_Max_Count"))
    return (max_emergency_count - requested_emergency_count)

def IsLeaveRequestValid(member_id, start_date, end_date):
    if end_date < start_date:
        return (False, (db.GetCaption(3)))

    if (len(utils.GetWorkDays(start_date, end_date)) <= 0):
        return (False, ("This request consists of Holidays/Weekends ONLY"))

    previously_requested_days = utils.FilterOutLeavesByStatus(GetRequestedLeavesBetween(member_id, start_date, end_date), "rejected")
    if len(previously_requested_days) > 0:
        return (False, (f"Leave request already exists for {utils.ConvertDatesToStrings(utils.GetDatesOfLeaves(previously_requested_days))}"))
        
    return (True, "Success")

async def InsertRetroactiveLeave(member, message_id, start_date, end_date, leave_type, is_requested_late, is_unpaid_retroactive, reason):
    is_request_valid, message = IsLeaveRequestValid(member.id, start_date, end_date)
    try:
        if is_request_valid:
            result = AddRetroactiveLeaveToDB(member, message_id, start_date, end_date, leave_type, "Approved", reason, is_requested_late, is_unpaid_retroactive)
            return result

        return message
    except Exception as e:
        print(e)
        return ("Something went wrong, please try again later")

def AddRetroactiveLeaveToDB(member, message_id, start_date, end_date, leave_type, leave_status, reason, is_emergency, is_unpaid):
    work_days = utils.GetWorkDays(start_date, end_date)
    remaining_emergency_count = GetRemainingEmergencyLeavesCount(member.id)
    annual_leave_balance = leave_db.GetAnnualLeaveBalance(member.id)
    for day in work_days:
        is_unpaid = ((is_unpaid) or (utils.IsUnpaidLeave(leave_type, annual_leave_balance, is_emergency, remaining_emergency_count)))
        if ((leave_type == "Annual") and not (is_unpaid)):
            annual_leave_balance -= 1
        leave_db.InsertLeave(member.id, message_id, leave_type, day, reason, "", leave_status, is_emergency, is_unpaid)
    return ("Retroactive leave was inserted successfully")

def GetLeavesAcrossRange(start_date, end_date, member):
    start_date = ConvertToISO8601(start_date)
    end_date = ConvertToISO8601(end_date)
    leaves_group = GroupLeavesBy(leave_db.GetLeavesBetween(start_date, end_date, member), 'member_id')
    ordered_leaves = []
    for leaves_array in leaves_group:
        leaves_sub_group = GroupLeavesBy(leaves_array, 'request_id')
        ordered_leaves.append(leaves_sub_group)
    return ordered_leaves

def GroupLeavesBy(leaves, col_name):
    ordered_leaves = collections.defaultdict(list)
    for leave in leaves:
        ordered_leaves[leave[col_name]].append(leave)
    return list(ordered_leaves.values())

def ConvertToISO8601(date_string):
    date = datetime.datetime.strptime(date_string, '%d/%m/%Y')
    return date.strftime("%Y-%m-%d")

def IsMemberWorking(member_id, date):
    work_days = utils.GetWorkDays(date, date)
    if len(work_days) <= 0:
        return (False, "Holiday/Weekend")

    is_member_on_leave, reason = IsMemberOnLeave(member_id, date)
    if is_member_on_leave:
        return (False, reason)
        
    return (True, "Member is working on the selected date")

def IsMemberOnLeave(member_id, date):
    approved_leaves = list(filter(lambda leave: leave['date'] == date and leave['leave_status'] == "Approved", leave_db.GetLeavesByMemberID(member_id)))
    if (len(approved_leaves) <= 0):
        return (False, "Member is working on the selected date")
    return (True, GetReasonOfLeaves(approved_leaves))   

def GetReasonOfLeaves(leaves_array):
    if len(leaves_array) <= 0:
        return None

    return leaves_array[0]["reason"]

async def AddEmojisToLeaveMessage(message):
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))
    await message.add_reaction(os.getenv("Revert_Emoji"))
