import Utilities
import os
import UI

from db import db
from Channels import Channels
from datetime import date, timedelta, datetime

async def RequestLeave(ctx, client, leavetype, startdate, enddate):
    current_time = datetime.now().hour
    if ValidateDates(startdate, enddate):
        if CheckAvailableBalance(startdate, enddate, leavetype):
            if current_time >= 12:
                await WarnRequester(ctx, client, startdate, enddate)
            else:
                await CompleteRequest(ctx, client, startdate, enddate, leavetype)

        else:
            await ctx.send(content = db.GetCaption(2) + str(int(os.getenv("Abdo_Annual_Leaves"))))

    else:
        await ctx.send(content = db.GetCaption(3))

async def WarnRequester(ctx, client, startdate, enddate):
    await ctx.send(content = db.GetCaption(7))
    message = await ctx.author.send(embed = UI.CreateWarningEmbed())
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))

    def check(reaction):
        return (reaction.message_id == message.id) and (str(reaction.emoji) in [os.getenv("Approve_Emoji"), os.getenv("Reject_Emoji")])
    
    reaction = await client.wait_for('raw_reaction_add', check = check, timeout = 120.0)

    if str(reaction.emoji) == os.getenv("Approve_Emoji"):
        await CompleteRequest(ctx, client, startdate, enddate, 2)

async def CompleteRequest(ctx, client, startdate, enddate, leaveType):
    await ctx.send(content = db.GetCaption(1))
    embed = UI.CreateLeaveEmbed(ctx, startdate, enddate, leaveType)
    channel = await Channels.GetLeaveApprovalsChannel(client)
    message = await channel.send(embed = embed)
    await message.add_reaction(os.getenv("Approve_Emoji"))
    await message.add_reaction(os.getenv("Reject_Emoji"))

async def HandleLeaveReactions(client, payload):
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    embed = message.embeds[0]

    if Utilities.isNotBot(payload.member) and isLeaveRequest(embed) and isPending(embed):
        status = UI.ParseEmoji(payload.emoji)
        if status != "":
            await UI.UpdateEmbedLeaveStatus(message, embed, status)
            await payload.member.send(content = "Your request was " + status)

def isLeaveRequest(embed):
    leave_embed_title = "Leave Request"

    return leave_embed_title.lower() in embed.title.lower()

def CheckAvailableBalance(startdate: str, enddate: str, leavetype):
    requestedDays = GetRequestedDays(startdate, enddate)

    returnValues = {
        1: int(os.getenv("Abdo_Annual_Leaves")) - requestedDays,
        2: int(os.getenv("Abdo_Emergency_Leaves")) - requestedDays,
        3: int(os.getenv("Abdo_Sick_Leaves")) - requestedDays
    }

    return returnValues[leavetype] >= 0

def GetRequestedDays(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    total_days = []

    for i in range((eDate - sDate).days + 1):
        day = sDate + timedelta(days=i)
        if day.weekday() != 4 and day.weekday() != 5:
            total_days.append(day) 

    return len(total_days)

def ValidateDates(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    return eDate >= sDate

def isPending(embed):
    leave_status = next((f for f in embed.fields if f.name.lower() == "status"), None).value

    return leave_status.lower() == "pending"
