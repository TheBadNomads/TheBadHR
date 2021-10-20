import Utilities as utils
import os
import UI
import datetime

from Channels import Channels
from db import db
from Leave import leave_db

async def RequestLeave(ctx, member, client, leavetype, startdate, enddate, reason):
    if enddate < startdate:
        await ctx.send(content = db.GetCaption(3))
        return 

    previously_requested_days = utils.ConvertDatesToStrings(GetRequestedDaysBetween(member.id, startdate, enddate))
    if len(previously_requested_days) > 0:
        await ctx.send(content = f"Leave request already exists for {previously_requested_days}")
        return
        
    if not (utils.HasEnoughBalance(startdate, enddate, leave_db.GetLeaveBalance(member.id, leavetype))):
        await ctx.send(content = db.GetCaption(2) + leave_db.GetLeaveBalance(member.id, leavetype))
        return
    
    await CompleteRequest(ctx, member, client, startdate, enddate, leavetype, reason)            
    
async def CompleteRequest(ctx, member, client, startdate, enddate, leaveType, reason):
    await ctx.send(content = db.GetCaption(1))
    embed = UI.CreateLeaveEmbed(ctx, startdate, enddate, leaveType)
    channel = Channels.GetLeaveApprovalsChannel(client)
    message = await channel.send(embed = embed)
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))
    AddLeaveRequestToDB(member, message.id, startdate, enddate, leaveType, "Pending", reason)

def AddLeaveRequestToDB(member, message_id, startdate, enddate, leaveType, leaveStatus, reason):
    requested_days = utils.GetRequestedDays(startdate, enddate)
    emergency_balance = leave_db.GetLeaveBalance(member.id, "Emergency")
    for day in requested_days:
        if not (utils.IsLeaveRequestedAfterCore(day)):
            leave_db.InsertLeave(member.id, message_id, leaveType, day, reason, "", leaveStatus)
            continue
        if emergency_balance > 0:
            leave_db.InsertLeave(member.id, message_id, "Emergency", day, reason, "", leaveStatus)
        else:
            leave_db.InsertLeave(member.id, message_id, "Unpaid", day, reason, "", leaveStatus)
                
async def HandleLeaveReactions(client, payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    embed = message.embeds[0]
    if utils.isNotBot(payload.member) and utils.IsAdmin(payload.member) and leave_db.IsLeaveRequestPending(payload.message_id):
        status = UI.ParseEmoji(payload.emoji)
        if status != None:
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
    leaves = leave_db.GetLeavesByRequestID(message_id)
    UpdateLeaveBalance(leaves[0]["member_id"], leaves[0]["leave_type"], -1)
    leaves.remove(leaves[0])
    if len(leaves) > 0:
        UpdateLeaveBalance(leaves[0]["member_id"], leaves[0]["leave_type"], -len(leaves))    

def UpdateLeaveBalance(member_id, leave_type, added_balance):
    leave_db.UpdateLeaveBalance(member_id, leave_type, added_balance)

def GetRequestedDaysBetween(member_id, start_date, end_date):
    requested_days = utils.GetRequestedDays(start_date, end_date)
    already_applied_days = [d['date'] for d in leave_db.GetLeavesMemberID(member_id)]
    previously_requested_days = set(requested_days).intersection(already_applied_days)
    return previously_requested_days
                