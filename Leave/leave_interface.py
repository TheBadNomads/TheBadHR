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

    return message

async def SubmitRequest(ctx, member, client, start_date, end_date, leave_type, reason):
    message_id = await SendLeaveRequestToChannel(ctx, client, start_date, end_date, leave_type, reason)
    return AddLeaveRequestToDB(member, message_id, start_date, end_date, leave_type, "Pending", reason)
    
async def SendLeaveRequestToChannel(ctx, client, start_date, end_date, leave_type, reason):
    embed = UI.CreateLeaveEmbed(ctx, start_date, end_date, leave_type, reason)
    channel = Channels.GetLeaveApprovalsChannel(client)
    message = await channel.send(embed = embed)
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))
    return message.id

def AddLeaveRequestToDB(member, message_id, start_date, end_date, leave_type, leave_status, reason, is_late_entry = False):
    if message_id == None:
        return ("Failed")

    try:
        work_days = utils.GetWorkDays(start_date, end_date)
        remaining_emergency_count = GetRemainingEmergencyLeavesCount(member.id)
        leave_balance = leave_db.GetLeaveBalance(member.id, leave_type)
        for index, day in enumerate(work_days):
            is_emergency = False
            if (not (is_late_entry)):
                is_emergency = utils.IsEmergencyLeave(day, leave_type)
            elif (index == 0):
                is_emergency = True

            is_unpaid = utils.IsUnpaidLeave(leave_balance, is_emergency, remaining_emergency_count)
            if (not (is_unpaid)):
                leave_balance -= 1

            leave_db.InsertLeave(member.id, message_id, leave_type, day, reason, "", leave_status, is_emergency, is_unpaid)
        return (db.GetCaption(1))
    except Exception as e:
        print(e)
        return ("Failed")
                
async def HandleLeaveReactions(client, payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    embed = message.embeds[0]
    
    status = UI.ParseEmoji(payload.emoji)
    if status == None:
        return

    if utils.isNotBot(payload.member) and utils.IsAdmin(payload.member) and leave_db.IsLeaveRequestPending(payload.message_id):
        await UpdateLeaveStatus(client, payload, status, message, embed)

async def UpdateLeaveStatus(client, payload, status, message, embed):
    try:
        leave_db.UpdateLeaveStatus(payload.message_id, status)
        if status == "Approved":
            UpdateLeaveBalanceOfRequestID(payload.message_id)

        await UI.UpdateEmbedLeaveStatus(message, embed, status)
        member = await client.fetch_user(utils.GetMemberIDFromEmbed(embed))
        await member.send(content = "Your request was " + status)
    except Exception as e:
        print(e)

def UpdateLeaveBalanceOfRequestID(message_id):
    requested_leaves = leave_db.GetLeavesByRequestID(message_id)
    ordered_requested_leaves = collections.defaultdict(list)
    for leave in requested_leaves:
        ordered_requested_leaves[leave['leave_type']].append(leave)

    for leaves_array in list(ordered_requested_leaves.values()):
        leave_db.UpdateMultipleLeavesBalance(leaves_array)

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
        return (f"Leave request already exists for {utils.ConvertDatesToStrings(utils.GetDatesOfLeaves(previously_requested_days))}")
        
    return (True, "")

async def InsertLateLeave(member, message_id, start_date, end_date, leave_type, reason):
    is_request_valid, message = IsLeaveRequestValid(member.id, start_date, end_date)
    try:
        if is_request_valid:
            result = AddLeaveRequestToDB(member, message_id, start_date, end_date, leave_type, "Approved", reason, True)
            UpdateLeaveBalanceOfRequestID(message_id)
            return result

        return message
    except Exception as e:
        print(e)
        return ("Something went wrong, please try again later")
