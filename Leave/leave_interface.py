import Utilities as utils
import os
import UI

from Channels import Channels
from datetime import datetime
from db import db
from Leave import leave_db

async def RequestLeave(ctx, member, client, leavetype, startdate, enddate, reason):
    if utils.ValidateDates(startdate, enddate):
        if utils.CheckAvailableBalance(member, startdate, enddate, leavetype):
            await ProccessRequest(ctx, member, client, leavetype, startdate, enddate, reason)
        else:
            await ctx.send(content = db.GetCaption(2) + leave_db.GetLeaveBalance(member.id, leavetype))

    else:
        await ctx.send(content = db.GetCaption(3))

async def ProccessRequest(ctx, member, client, startdate, enddate, leavetype, reason):
    current_time = datetime.now().hour

    if ctx.author.id != member.id:
        await CompleteRequest(ctx, member, client, startdate, enddate, leavetype, reason)
        return
    
    if current_time < 12:
        await CompleteRequest(ctx, member, client, startdate, enddate, leavetype, reason)
        return

    if leavetype.lower() == "annual" or leavetype.lower() == "sick":
        await WarnRequester(ctx, member, client, startdate, enddate, reason)
        return

    await CompleteRequest(ctx, member, client, startdate, enddate, leavetype, reason)

async def WarnRequester(ctx, member, client, startdate, enddate, reason):
    await ctx.send(content = db.GetCaption(7))
    message = await ctx.author.send(embed = UI.CreateWarningEmbed())
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))

    def check(reaction):
        return (reaction.message_id == message.id) and (str(reaction.emoji) in [os.getenv("Approve_Emoji"), os.getenv("Reject_Emoji")])

    reaction = await client.wait_for('raw_reaction_add', check = check, timeout = 120.0)

    if str(reaction.emoji) == os.getenv("Approve_Emoji"):
        await CompleteRequest(ctx, member, client, startdate, enddate, "Emergency", reason)

async def CompleteRequest(ctx, member, client, startdate, enddate, leaveType, reason):
    await ctx.send(content = db.GetCaption(1))
    embed = UI.CreateLeaveEmbed(ctx, startdate, enddate, leaveType)
    channel = await Channels.GetLeaveApprovalsChannel(client)
    message = await channel.send(embed = embed)
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))

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
            try:
                leave_db.UpdateLeaveStatus(payload.message_id, status)
                await UI.UpdateEmbedLeaveStatus(message, embed, status)
                await payload.member.send(content = "Your request was " + status)

                if status == "Approved":
                    leaves = leave_db.GetLeaveByRequestID(payload.message_id)
                    leave = leaves[0]
                    leave_db.UpdateLeaveBalance(payload.member.id, leave["leave_type"], -len(leaves))

            except Exception as e:
                print(e)
            