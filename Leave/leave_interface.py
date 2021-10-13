import Utilities as utils
import os
import UI
import datetime

from Channels import Channels
from db import db
from Leave import leave_db

async def RequestLeave(ctx, member, client, leavetype, startdate, enddate, reason):
    perviously_requested_days = GetPerviouslyRequestedDays(member.id, startdate, enddate)

    if len(perviously_requested_days) > 0:
        await ctx.send(content = f"Leave request already exists for {perviously_requested_days}")
        return
    
    if utils.IsDateOrderValid(startdate, enddate):
        if utils.HasEnoughBalance(startdate, enddate, leave_db.GetLeaveBalance(member.id, leavetype)):
            await ProccessRequest(ctx, member, client, startdate, enddate, leavetype, reason)
        else:
            await ctx.send(content = db.GetCaption(2) + leave_db.GetLeaveBalance(member.id, leavetype))
    else:
        await ctx.send(content = db.GetCaption(3))

async def ProccessRequest(ctx, member, client, startdate, enddate, leavetype, reason):
    current_hour = datetime.datetime.now().time()
    end_of_core = datetime.time(13)
    today = datetime.datetime.today().date()
    
    if (startdate.date() == today) or ((current_hour >= end_of_core) and (startdate.date() == today + datetime.timedelta(1))):
        await CompleteSpecialRequest(ctx, member, client, startdate, enddate, leavetype, reason)
        return

    await CompleteRequest(ctx, member, client, startdate, enddate, leavetype, reason)

async def CompleteSpecialRequest(ctx, member, client, startdate, enddate, leavetype, reason):
    requested_days = utils.GetRequestedDays(startdate, enddate)

    if leave_db.GetLeaveBalance(member.id, "Emergency") > 0:
        await CompleteRequest(ctx, member, client, requested_days[0], requested_days[0], "Emergency", reason)
    else:
        await CompleteRequest(ctx, member, client, requested_days[0], requested_days[0], "Unpaid", reason)
    
    if len(requested_days) > 1:
        await CompleteRequest(ctx, member, client, requested_days[1], enddate, leavetype, reason)
    

async def CompleteRequest(ctx, member, client, startdate, enddate, leaveType, reason):
    await ctx.send(content = db.GetCaption(1))
    embed = UI.CreateLeaveEmbed(ctx, startdate, enddate, leaveType)
    channel = Channels.GetLeaveApprovalsChannel(client)
    message = await channel.send(embed = embed)
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))
    CompleteRequest_DB(member, message.id, startdate, enddate, leaveType, "Pending", reason)

def CompleteRequest_DB(member, message_id, startdate, enddate, leaveType, leaveStatus, reason):
    requested_days = utils.GetRequestedDays(startdate, enddate)

    for day in requested_days:
        leave_db.InsertLeave(member.id, message_id, leaveType, day, reason, "", leaveStatus)

async def HandleLeaveReactions(client, payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    embed = message.embeds[0]

    if utils.isNotBot(payload.member) and utils.IsAdmin(payload.member) and leave_db.IsLeaveRequest(payload.message_id) and leave_db.IsLeaveRequestPending(payload.message_id):
        status = UI.ParseEmoji(payload.emoji)
        if status != None:
            await UpdateLeaveStatus(client, payload, status, message, embed)
            if status == "Approved":
                UpdateLeaveBalance(payload.message_id)

async def UpdateLeaveStatus(client, payload, status, message, embed):
    try:
        leave_db.UpdateLeaveStatus(payload.message_id, status)
        await UI.UpdateEmbedLeaveStatus(message, embed, status)
        member = await client.fetch_user(leave_db.GetLeavesByRequestID(payload.message_id)[0]["member_id"])
        await member.send(content = "Your request was " + status)

    except Exception as e:
        print(e)

def UpdateLeaveBalance(message_id):
    leaves = leave_db.GetLeavesByRequestID(message_id)
    leave = leaves[0]
    leave_db.UpdateLeaveBalance(leave["member_id"], leave["leave_type"], -len(leaves))

def GetPerviouslyRequestedDays(member_id, start_date, end_date):
    reqested_days = utils.GetRequestedDays(start_date, end_date)
    already_applied_days = [d['date'] for d in leave_db.GetLeavesDatesByMemberID(member_id)]
    perviously_requested_days = []

    for day in reqested_days:
        if day in already_applied_days:
            perviously_requested_days.append(day.strftime('%d/%m/%Y'))
    
    return perviously_requested_days
                