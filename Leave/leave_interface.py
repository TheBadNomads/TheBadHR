import Utilities as utils
import os
import UI
import discord
import datetime

from Channels import Channels
from db import db
from Leave import leave_db

async def RequestLeave(ctx, member, client, leavetype, startdate, enddate, reason):
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
    role = discord.utils.find(lambda r: r.name == 'Admin', ctx.guild.roles)

    if role in ctx.author.roles:
        CompleteRequest_DB(member, 0, startdate, enddate, leavetype, "Approved", reason)
        await ctx.send(content = "Success")
        return
    
    if current_hour >= end_of_core or (startdate == datetime.datetime.today()):
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
        leave_db.InsertLeave(member.id, message_id, leaveType, day, reason, "", leaveStatus)

async def HandleLeaveReactions(client, payload):
    await HandleNormalRequest(client, payload)

async def HandleNormalRequest(client, payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    embed = message.embeds[0]

    if utils.isNotBot(payload.member) and leave_db.IsLeaveRequest(payload.message_id) and leave_db.IsLeaveRequestPending(payload.message_id):
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
    leaves = leave_db.GetLeavesByRequestID(payload.message_id)
    leave = leaves[0]
    leave_db.UpdateLeaveBalance(payload.member.id, leave["leave_type"], -len(leaves))
                