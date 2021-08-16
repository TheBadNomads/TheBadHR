from aiohttp.client import request
import discord
import os
import db
import member_module as mm
import leave_module as lm

from datetime import date, timedelta, datetime
from discord_slash.utils.manage_commands import create_option, create_choice

#Embeds
def CreateLeaveEmbed(ctx, startdate, enddate, leaveType):
    leaveTypes = {
        1: "Annual",
        2: "Emergency",
        3: "Sick"
    }

    leaveImages = {
        1: os.getenv("Annual_Leave_Link"),
        2: os.getenv("Emergency_Leave_Link"),
        3: os.getenv("Sick_Leave_Link")
    }

    embed = discord.Embed(
        title = leaveTypes[leaveType] + " Leave Request", 
        description = f'{ctx.author.mention} is requesting '+ leaveTypes[leaveType].lower() +' leave', 
        colour = 0x4682B4
    )

    embed.set_thumbnail(url = leaveImages[leaveType])
    embed.add_field(name = "Start Date", value = startdate, inline = True)
    embed.add_field(name = "End Date", value = enddate, inline = True)
    embed.add_field(name = '\u200B', value = '\u200B', inline = False)
    embed.add_field(name = "Status", value = "Pending", inline = False)
    embed.set_footer(text = date.today())

    return embed

def CreateWarningEmbed():
    embed = discord.Embed(
        title = "Warning !!!!!", 
        description = db.GetCaption(8), 
        colour = 0xFF0000
    )

    return embed

#Choises
def CreateLeaveTypeChoices():
    leaveTypeChoices = []
    for type in lm.GetLeaveTypes():
        leaveTypeChoices.append(create_choice(name = type[1], value = type[0]))

    return leaveTypeChoices

def CreatePositionChoices():
    positionChoices = []
    for type in mm.GetPositions():
        positionChoices.append(create_choice(name = type[1], value = type[0]))

    return positionChoices

def CreateDateChoices():
    firstDate = date.today() + timedelta(1)
    dateChoices = []
    
    for i in range(25):
        tmpDate = firstDate + timedelta(i)
        weekDay = tmpDate.strftime("%A")
        dateChoices.append(create_choice(name = weekDay +": "+ tmpDate.strftime('%m/%d/%Y'), value = tmpDate.strftime('%m/%d/%Y')))
    
    return dateChoices

def CreateDateOptions():
    requestLeave_options = [
        create_option(
            name = "leavetype",
            description = "leave type",
            option_type = 4,
            required = True,
            choices = CreateLeaveTypeChoices()
        ),
        create_option(
            name = "startdate",
            description = "starting date of your leave",
            option_type = 3,
            required = True,
            choices = CreateDateChoices()
        ),
        create_option(
            name = "enddate",
            description = "ending date of your leave",
            option_type = 3,
            required = True,
            choices = CreateDateChoices()
        ),
        create_option(
            name = "reason",
            description = "reason for the leave (optional)",
            option_type = 3,
            required = False
        )
    ]

    return requestLeave_options

def CreateMemberOptions():
    member_options = [
        create_option(
            name = "discorduser",
            description = "discord user",
            option_type = 6,
            required = True
        ),
        create_option(
            name = "name",
            description = "name",
            option_type = 3,
            required = True
        ),
        create_option(
            name = "email",
            description = "email",
            option_type = 3,
            required = True
        ),
        create_option(
            name = "startdate",
            description = "working start date format: m/d/y",
            option_type = 3,
            required = True
        ),
        create_option(
            name = "leavedate",
            description = "working leave date format: m/d/y",
            option_type = 3,
            required = True
        ),
        create_option(
            name = "position",
            description = "member position",
            option_type = 4,
            required = True,
            choices = CreatePositionChoices()
        ),
    ]

    return member_options

def CreateBalanceOptions():
    balance_options = [
        create_option(
            name = "leavetype",
            description = "leave type",
            option_type = 4,
            required = True,
            choices = CreateLeaveTypeChoices()
        )
    ]

    return balance_options

#Helper Functions
async def HandleLeaveReactions(client, payload):
    channel = await client.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    embed = message.embeds[0]

    if CheckBotUser(payload.member) and CheckCorrectChannel(payload.channel_id) and CheckCorrectMessage(payload.message_id) and CheckLeaveStatus(payload.message_id):
        status = HandleEmoji(payload)
        if status != "":
            await ChangeLeaveStatus(message, embed, status)
            await payload.member.send(content = "Your request was " + status)

async def WarnRequester(ctx, client, startdate, enddate, leavesChannel, reason):
    await ctx.send(content = db.GetCaption(7))
    message = await ctx.author.send(embed = CreateWarningEmbed())
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    def check(reaction):
        return (reaction.message_id == message.id) and (reaction.user_id == ctx.author.id) and (str(reaction.emoji) in ["✅", "❌"])
    
    reaction = await client.wait_for('raw_reaction_add', check=check)

    if str(reaction.emoji) == "✅":
        await CompleteRequest(ctx, startdate, enddate, leavesChannel, 2, reason)

async def CompleteRequest(ctx, startdate, enddate, leavesChannel, leaveType, reason):
    await ctx.send(content = db.GetCaption(1))
    embed = CreateLeaveEmbed(ctx, startdate, enddate, leaveType)
    message = await leavesChannel.send(embed = embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    member = mm.GetMemeberByID(ctx.author.id)
    requested_days = lm.GetRequestedDays(startdate, enddate)

    for day in requested_days:
        lm.InsertLeave(member.id, message.id, leaveType, "pending", day, reason, "")

async def ChangeLeaveStatus(message, embed, newStatus):
    embed_dict = embed.to_dict()

    for field in embed_dict["fields"]:
        if field["name"].lower() == "status":
            field["value"] = newStatus

    embed = discord.Embed.from_dict(embed_dict)
    await message.edit(embed=embed)
    
    lm.UpdateLeaveStatus(message.id, newStatus)

def CheckCorrectChannel(channel_id):
    return channel_id == int(os.getenv("TestChannel_id"))

def CheckCorrectMessage(message_id):
    return len(lm.GetLeaveByRequestID(message_id)) != 0

def CheckLeaveStatus(message_id):
    return lm.GetLeaveStatus(message_id) == "pending"

def CheckBotUser(member):
    return not member.bot

def HandleEmoji(payload):
    emoji_str = str(payload.emoji)

    if emoji_str == '✅':
        leaves = lm.GetLeaveByRequestID(payload.message_id)
        lm.UpdateLeaveBalance(leaves[0].member_id, leaves[0].leave_type, len(leaves) * -1)

        return "Approved"

    elif emoji_str == '❌':
        return "Rejected"

    return ""