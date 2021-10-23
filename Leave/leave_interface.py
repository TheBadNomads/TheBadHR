import Utilities as utils
import os
import UI
import collections

from Channels import Channels
from db import db
from Leave import leave_db

async def RequestLeave(ctx, member, client, leave_type, start_date, end_date, reason):
    if end_date < start_date:
        await ctx.send(content = db.GetCaption(3))
        return 

    repeated_requested_days = utils.ConvertDatesToStrings(GetRepeatedRequestedDaysBetween(member.id, start_date, end_date))
    if len(repeated_requested_days) > 0:
        await ctx.send(content = f"Leave request already exists for {repeated_requested_days}")
        return
    
    leave_balance = leave_db.GetLeaveBalance(member.id, leave_type)
    if not (utils.HasEnoughBalance(start_date, end_date, leave_balance)):
        await ctx.send(content = db.GetCaption(2) + leave_balance)
        return
    
    await CompleteRequest(ctx, member, client, start_date, end_date, leave_type, reason)            
    
async def CompleteRequest(ctx, member, client, start_date, end_date, leave_type, reason):
    await ctx.send(content = db.GetCaption(1))
    embed = UI.CreateLeaveEmbed(ctx, start_date, end_date, leave_type)
    channel = Channels.GetLeaveApprovalsChannel(client)
    message = await channel.send(embed = embed)
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))
    AddLeaveRequestToDB(member, message.id, start_date, end_date, leave_type, "Pending", reason)

def AddLeaveRequestToDB(member, message_id, start_date, end_date, leave_type, leave_status, reason):
    requested_days = utils.GetRequestedDays(start_date, end_date)
    emergency_balance = leave_db.GetLeaveBalance(member.id, "Emergency")
    for day in requested_days:
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
    requested_leaves = leave_db.GetLeavesByRequestID(message_id)
    ordered_requested_leaves = collections.defaultdict(list)
    for leave in requested_leaves:
        ordered_requested_leaves[leave['leave_type']].append(leave)

    for leaves_array in list(ordered_requested_leaves.values()):
        leave_db.UpdateLeaveBalance(leaves_array[0]["member_id"], leaves_array[0]["leave_type"], -len(leaves_array))

def GetRepeatedRequestedDaysBetween(member_id, start_date, end_date):
    current_requested_days = utils.GetRequestedDays(start_date, end_date)
    previously_requested_days = [d['date'] for d in leave_db.GetLeavesMemberID(member_id)]
    repeated_requested_days = set(current_requested_days).intersection(previously_requested_days)
    return repeated_requested_days
