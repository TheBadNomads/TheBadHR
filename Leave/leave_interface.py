import Utilities as utils
import os
import UI
import discord

from Channels import Channels
from datetime import datetime
from db import db
from Leave import leave_db

async def RequestLeave(ctx, member, client, leavetype, startdate, enddate, reason):
    if utils.ValidateDates(startdate, enddate):
        if utils.CheckAvailableBalance(member, startdate, enddate, leavetype):
            await ProccessRequest(ctx, member, client, startdate, enddate, leavetype, reason)
        else:
            await ctx.send(content = db.GetCaption(2) + leave_db.GetLeaveBalance(member.id, leavetype))

    else:
        await ctx.send(content = db.GetCaption(3))

async def ProccessRequest(ctx, member, client, startdate, enddate, leavetype, reason):
    current_hour = datetime.now().hour
    role = discord.utils.find(lambda r: r.name == 'Admin', ctx.guild.roles)

    # if role in ctx.author.roles:
    #     CompleteRequest_DB(member, 0, startdate, enddate, leavetype, "Approved", reason)
    #     return
    
    if current_hour > 12:
        if leavetype.lower() == "annual" or leavetype.lower() == "sick":
            await CompleteRequest(ctx, member, client, startdate, enddate, "Emergency", reason)
            return

    await CompleteRequest(ctx, member, client, startdate, enddate, leavetype, reason)

async def CompleteRequest(ctx, member, client, startdate, enddate, leaveType, reason):
    await ctx.send(content = db.GetCaption(1))
    embed = UI.CreateLeaveEmbed(ctx, startdate, enddate, leaveType)
    channel = await Channels.GetLeaveApprovalsChannel(client)
    message = await channel.send(embed = embed)
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))
    CompleteRequest_DB(member, message.id, startdate, enddate, leaveType, "Pending", reason)

def CompleteRequest_DB(member, message_id, startdate, enddate, leaveType, leaveStatus, reason):
    requested_days = utils.GetRequestedDays(startdate, enddate)

    for day in requested_days:
        leave_db.InsertLeave(member.id, message_id, leaveType, leaveStatus, day, reason, "")

async def HandleLeaveReactions(client, payload):
    await HandleNormalRequest(client, payload)

async def HandleNormalRequest(client, payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    embed = message.embeds[0]

    if utils.isNotBot(payload.member) and utils.isLeaveRequest(payload.message_id) and utils.isPending(payload.message_id):
        status = UI.ParseEmoji(payload.emoji)
        if status != None:
            await UpdateLeaveStatus(payload, status, message, embed)
            if status == "Approved":
                UpdateLeaveBalance(payload)

async def UpdateLeaveStatus(payload, status, message, embed):
    try:
        leave_db.UpdateLeaveStatus(payload.message_id, status)
        await UI.UpdateEmbedLeaveStatus(message, embed, status)
        await payload.member.send(content = "Your request was " + status)

    except Exception as e:
        print(e)

def UpdateLeaveBalance(payload):
    leaves = leave_db.GetLeaveByRequestID(payload.message_id)
    leave = leaves[0]
    leave_db.UpdateLeaveBalance(payload.member.id, leave["leave_type"], -len(leaves))
                