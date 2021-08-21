import leave_utils as lu
import Utilities
import os
import UI

from Channels import Channels
from datetime import datetime
from leave_db import leave
from leave_type_db import LeaveType
from Member import member_interface as mi

async def RequestLeave(ctx, client, leavetype, startdate, enddate, reason):
    current_time = datetime.now().hour
    if lu.ValidateDates(startdate, enddate):
        if lu.CheckAvailableBalance(startdate, enddate, leavetype):
            if current_time >= 12:
                await WarnRequester(ctx, client, startdate, enddate, reason)
            else:
                await CompleteRequest(ctx, client, startdate, enddate, leavetype, reason)

        else:
            await ctx.send(content = UI.GetCaption(2) + str(int(os.getenv("Abdo_Annual_Leaves"))))

    else:
        await ctx.send(content = UI.GetCaption(3))

async def WarnRequester(ctx, client, startdate, enddate, reason):
    await ctx.send(content = UI.GetCaption(7))
    message = await ctx.author.send(embed = UI.CreateWarningEmbed())
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))

    def check(reaction):
        return (reaction.message_id == message.id) and (str(reaction.emoji) in [os.getenv("Approve_Emoji"), os.getenv("Reject_Emoji")])
    
    reaction = await client.wait_for('raw_reaction_add', check = check, timeout = 120.0)

    if str(reaction.emoji) == os.getenv("Approve_Emoji"):
        await CompleteRequest(ctx, client, startdate, enddate, 2, reason)

async def CompleteRequest(ctx, client, startdate, enddate, leaveType, reason):
    await ctx.send(content = UI.GetCaption(1))
    embed = UI.CreateLeaveEmbed(ctx, startdate, enddate, leaveType)
    channel = await Channels.GetLeaveApprovalsChannel(client)
    message = await channel.send(embed = embed)
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))

    member = mi.GetMemeberByID(ctx.author.id)
    requested_days = lu.GetRequestedDays(startdate, enddate)

    for day in requested_days:
        leave.InsertLeave(member.id, message.id, leaveType, "pending", day, reason, "")

async def HandleLeaveReactions(client, payload):
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    embed = message.embeds[0]

    if Utilities.isNotBot(payload.member) and lu.isLeaveRequest(payload.message_id) and lu.isPending(payload.message_id):
        status = UI.ParseEmoji(payload.emoji)
        if status != "":
            leave.UpdateLeaveStatus(payload.message_id, status)
            await UI.UpdateEmbedLeaveStatus(message, embed, status)
            await payload.member.send(content = "Your request was " + status)

def GetLeaveTypes():
    return LeaveType.GetLeaveTypes()

def GetLeaveBalance(member_id, leave_type):
    return leave.GetLeaveBalance(member_id, leave_type)
