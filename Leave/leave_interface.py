import datetime
import Utilities as utils
import os
import UI
import collections

from Channels import Channels
from db import db
from Leave import leave_db

async def ProcessLeaveRequest(ctx, member, client, leave_type, start_date, end_date, reason):
    if end_date < start_date:
        await ctx.send(content = db.GetCaption(3))
        return 

    repeated_requested_days = utils.ConvertDatesToStrings(GetRequestedDaysBetween(member.id, start_date, end_date))
    if len(repeated_requested_days) > 0:
        await ctx.send(content = f"Leave request already exists for {repeated_requested_days}")
        return
    
    await SubmitRequest(ctx, member, client, start_date, end_date, leave_type, reason)            

async def SubmitRequest(ctx, member, client, start_date, end_date, leave_type, reason):
    message_id = await SendLeaveRequestToChannel(ctx, client, start_date, end_date, leave_type, reason)
    AddLeaveRequestToDB(member, message_id, start_date, end_date, leave_type, "Pending", reason)
    
async def SendLeaveRequestToChannel(ctx, client, start_date, end_date, leave_type, reason):
    await ctx.send(content = db.GetCaption(1))
    embed = UI.CreateLeaveEmbed(ctx, start_date, end_date, leave_type, reason)
    channel = Channels.GetLeaveApprovalsChannel(client)
    message = await channel.send(embed = embed)
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))
    return message.id

def AddLeaveRequestToDB(member, message_id, start_date, end_date, leave_type, leave_status, reason):
    work_days = utils.GetWorkDays(start_date, end_date)
    remaining_emergency_count = GetRemainingEmergencyLeavesCount(member.id)
    leave_balance = leave_db.GetLeaveBalance(member.id, leave_type)
    for day in work_days:
        adjusted_leave_type = leave_type
        is_emergency = False
        if ((utils.IsLateToApplyForLeave(day)) and (leave_type.lower() != "sick")):
            is_emergency = True
        if ((leave_balance <= 0) or ((is_emergency) and (remaining_emergency_count <= 0))):
            adjusted_leave_type = "Unpaid"
        else:
            leave_balance -= 1

        leave_db.InsertLeave(member.id, message_id, adjusted_leave_type, day, reason, "", leave_status, is_emergency)
                
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

def GetRequestedDaysBetween(member_id, start_date, end_date):
    work_days = utils.GetWorkDays(start_date, end_date)
    previous_leaves = leave_db.GetLeavesByMemberID(member_id)
    previously_requested_days = [d['date'] for d in utils.FilterOutLeavesByStatus(previous_leaves, "rejected")]
    requested_days = set(work_days).intersection(previously_requested_days)
    return requested_days

def GetRemainingEmergencyLeavesCount(member_id):
    requested_emergency_count = len(leave_db.GetEmergencyLeavesForYear(member_id, datetime.date.today().year))
    max_emergency_count = int(os.getenv("Emergency_Leaves_Max_Count"))
    return (max_emergency_count - requested_emergency_count)
