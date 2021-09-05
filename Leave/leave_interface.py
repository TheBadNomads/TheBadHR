import Utilities as utils
import os
import UI

from Channels import Channels
from datetime import datetime
from db import db
from Leave import leave_db
from Member import member_db

async def RequestLeave(ctx, client, leavetype, startdate, enddate, reason):
    current_time = datetime.now().hour
    if utils.ValidateDates(startdate, enddate):
        if utils.CheckAvailableBalance(startdate, enddate, leavetype):
            if current_time >= 12:
                await WarnRequester(ctx, client, startdate, enddate, reason)
            else:
                await CompleteRequest(ctx, client, startdate, enddate, leavetype, reason)

        else:
            await ctx.send(content = db.GetCaption(2) + leave_db.GetLeaveBalance(ctx.author.id, leavetype))

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

    member = member_db.GetMemberByID(ctx.author.id)
    requested_days = utils.GetRequestedDays(startdate, enddate)

    for day in requested_days:
        leave_db.InsertLeave(member.id, message.id, leaveType, "pending", day, reason, "")

async def HandleLeaveReactions(client, payload):
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    embed = message.embeds[0]

    if utils.isNotBot(payload.member) and utils.isLeaveRequest(payload.message_id) and utils.isPending(payload.message_id):
        status = UI.ParseEmoji(payload.emoji)
        if status != "":
            leave_db.UpdateLeaveStatus(payload.message_id, status)
            await UI.UpdateEmbedLeaveStatus(message, embed, status)
            await payload.member.send(content = "Your request was " + status)