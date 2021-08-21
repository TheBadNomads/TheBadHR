import Utilities
import os
import UI
import sys
sys.path.append(".")

from Channels import Channels
from datetime import datetime
from db import db
from .leave_db import leave
from .leave_type_db import LeaveType
from .leave_utils import *
from Member import member_interface as mi

async def RequestLeave(ctx, client, leavetype, startdate, enddate, reason):
    current_time = datetime.now().hour
    if ValidateDates(startdate, enddate):
        if CheckAvailableBalance(startdate, enddate, leavetype):
            if current_time >= 12:
                await WarnRequester(ctx, client, startdate, enddate, reason)
            else:
                await CompleteRequest(ctx, client, startdate, enddate, leavetype, reason)

        else:
            await ctx.send(content = db.GetCaption(2) + leave.GetLeaveBalance(ctx.author.id, leavetype))

    else:
        await ctx.send(content = db.GetCaption(3))

async def WarnRequester(ctx, client, startdate, enddate, reason):
    await ctx.send(content = db.GetCaption(7))
    message = await ctx.author.send(embed = UI.CreateWarningEmbed())
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))

    def check(reaction):
        return (reaction.message_id == message.id) and (str(reaction.emoji) in [os.getenv("Approve_Emoji"), os.getenv("Reject_Emoji")])
    
    reaction = await client.wait_for('raw_reaction_add', check = check, timeout = 120.0)

    if str(reaction.emoji) == os.getenv("Approve_Emoji"):
        await CompleteRequest(ctx, client, startdate, enddate, 2, reason)

async def CompleteRequest(ctx, client, startdate, enddate, leaveType, reason):
    await ctx.send(content = db.GetCaption(1))
    embed = UI.CreateLeaveEmbed(ctx, startdate, enddate, leaveType)
    channel = await Channels.GetLeaveApprovalsChannel(client)
    message = await channel.send(embed = embed)
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))

    member = mi.GetMemberByID(ctx.author.id)
    requested_days = GetRequestedDays(startdate, enddate)

    for day in requested_days:
        leave.InsertLeave(member.id, message.id, leaveType, "pending", day, reason, "")

async def HandleLeaveReactions(client, payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    embed = message.embeds[0]

    if Utilities.isNotBot(payload.member) and isLeaveRequest(payload.message_id) and isPending(payload.message_id):
        status = UI.ParseEmoji(payload.emoji)
        if status != "":
            leave.UpdateLeaveStatus(payload.message_id, status)
            await UI.UpdateEmbedLeaveStatus(message, embed, status)
            await payload.member.send(content = "Your request was " + status)

def GetLeaveTypes():
    return LeaveType.GetLeaveTypes()

def GetLeaveBalance(member_id, leave_type):
    return leave.GetLeaveBalance(member_id, leave_type)

def InsertLeaveBalance(member_id:int, start_date:datetime):
    return leave.InsertLeaveBalance(member_id, start_date)
