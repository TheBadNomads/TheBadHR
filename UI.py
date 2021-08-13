import discord
import os
import db

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
        description = GetCaption(8), 
        colour = 0xFF0000
    )

    return embed

#Choises
def CreateLeaveTypeChoices():
    leaveTypeChoices = []
    leaveTypeChoices.append(create_choice(name = "Annual", value = 1))
    leaveTypeChoices.append(create_choice(name = "Emergency", value = 2))
    leaveTypeChoices.append(create_choice(name = "Sick", value = 3))

    return leaveTypeChoices

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
            description = "Leave empty for 1 day leave",
            option_type = 3,
            required = True,
            choices = CreateDateChoices()
        )
    ]

    return requestLeave_options

def CreateUserOptions():
    user_options = [
        create_option(
            name = "firstname",
            description = "first name",
            option_type = 3,
            required = True
        ),
        create_option(
            name = "lastname",
            description = "last name",
            option_type = 3,
            required = True
        ),
        create_option(
            name = "discorduser",
            description = "discord user",
            option_type = 6,
            required = True
        ),
        create_option(
            name = "annualbalance",
            description = "Annual Balance",
            option_type = 10,
            required = True
        ),
        create_option(
            name = "emergencybalance",
            description = "Emergency Balance",
            option_type = 10,
            required = True
        ),
        create_option(
            name = "sickbalance",
            description = "Sick Balance",
            option_type = 10,
            required = True
        )
    ]

    return user_options

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

    if CheckCorrectChannel(payload.channel_id) and CheckCorrectMessage(payload.message_id) and CheckLeaveStatus(payload.message_id) and CheckBotUser(payload.member):
        status = HandleEmoji(payload.emoji)
        if status != "":
            await ChangeLeaveStatus(message, embed, status)
            await payload.member.send(content = "Your request was " + status)

async def WarnRequester(ctx, client, startdate, enddate, leavesChannel):
    await ctx.send(content = GetCaption(7))
    message = await ctx.author.send(embed = CreateWarningEmbed())
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    def check(reaction):
        return (reaction.message_id == message.id) and (reaction.user_id == ctx.author.id) and (str(reaction.emoji) in ["✅", "❌"])
    
    reaction = await client.wait_for('raw_reaction_add', check=check)

    if str(reaction.emoji) == "✅":
        await CompleteRequest(ctx, startdate, enddate, leavesChannel, 2)

async def CompleteRequest(ctx, startdate, enddate, leavesChannel, leaveType):
    await ctx.send(content = GetCaption(1))
    embed = CreateLeaveEmbed(ctx, startdate, enddate, leaveType)
    message = await leavesChannel.send(embed = embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

    user = db.GetUserByID(ctx.author.id)

    db.InsertLeave(user[0], leaveType, message.id, "pending")

async def ChangeLeaveStatus(message, embed, newStatus):
    embed_dict = embed.to_dict()

    for field in embed_dict["fields"]:
        if field["name"].lower() == "status":
            field["value"] = newStatus

    embed = discord.Embed.from_dict(embed_dict)

    await message.edit(embed=embed)

    db.UpdateLeaveStatus(message.id, newStatus)

def CheckCorrectChannel(channel_id):
    return channel_id == int(os.getenv("TestChannel_id"))

def CheckCorrectMessage(message_id):
    return db.GetLeaveByID(message_id) != None

def CheckLeaveStatus(message_id):
    return db.GetLeaveStatus(message_id) == "pending"

def CheckBotUser(member):
    return not member.bot

def HandleEmoji(emoji):
    emoji_str = str(emoji)

    if emoji_str == '✅':
        return "Approved"

    elif emoji_str == '❌':
        return "Rejected"

    return ""

# to be changed to get captions from DB 
def GetCaption(captionCode):
    switcher = {
        1: "Your leave request has been sent",
        2: "You dont have enough leaves to request, your current balance is ",
        3: "Please select valid dates",
        4: "Your Request has failed, try again later",
        5: "Your annual leave request was approved",
        6: "Your annual leave request was rejected",
        7: "Your request is being processed",
        8: "It is past core hours your leave request with be considered as an emergency leave",
        9: "Your emergency leave request was approved",
        10: "Your emergency leave request was rejected",
        11: "Your sick leave request was approved",
        12: "Your sick leave request was rejected",
    }

    return switcher.get(captionCode, lambda: "Invalid caption code")