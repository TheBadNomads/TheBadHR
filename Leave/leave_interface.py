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
    
    leave_balance = leave_db.GetLeaveBalance(member.id, leave_type)
    if not (utils.HasEnoughBalance(start_date, end_date, leave_balance)):
        await ctx.send(content = db.GetCaption(2) + leave_balance)
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
    emergency_balance = leave_db.GetLeaveBalance(member.id, "Emergency")
    for day in work_days:
        if not (utils.IsLateToApplyForLeave(day)):
            leave_db.InsertLeave(member.id, message_id, leave_type, day, reason, "", leave_status)
            continue
        if emergency_balance > 0:
            leave_db.InsertLeave(member.id, message_id, "Emergency", day, reason, "", leave_status)
        else:
            leave_db.InsertLeave(member.id, message_id, "Unpaid", day, reason, "", leave_status)
                
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
    previous_leaves = leave_db.GetLeavesMemberID(member_id)
    previously_requested_days = [d['date'] for d in utils.FilterOutLeavesByStatus(previous_leaves, "rejected")]
    requested_days = set(work_days).intersection(previously_requested_days)
    return requested_days

async def ApplyLateLeave(ctx, member, start_date, end_date, leave_type, reason):
    work_days = utils.GetWorkDays(start_date, end_date)
    if len(work_days) == 0:
        await ctx.send(content = "The requested dates are weekends/holidays")
        return

    requested_days = utils.ConvertDatesToStrings(GetRequestedDaysBetween(member.id, start_date, end_date))
    if len(requested_days) > 0:
        await ctx.send(content = f"Leave request already exists for {requested_days}")
        return

    requested_leave_balance = leave_db.GetLeaveBalance(member.id, leave_type)
    message = await ctx.send(content = "Late leave is being processed...")
    try:
        InsertLateLeaveIntoDB(member, message.id, work_days, leave_type, requested_leave_balance, reason)
        UpdateLeaveBalanceOfRequestID(message.id)
        await message.edit(content = "Late leave was inserted successfully")
    except Exception as e:
        await message.edit(content = "Something went wrong, please try again later")
        print(e)

def InsertLateLeaveIntoDB(member, message_id, work_days, leave_type, requested_leave_balance, reason):
    for day in work_days:
        if requested_leave_balance > 0:
            leave_db.InsertLeave(member.id, message_id, leave_type, day, reason, "", "Approved")
            requested_leave_balance -= 1
        else:
            leave_db.InsertLeave(member.id, message_id, "Unpaid", day, reason, "", "Approved")
    return
