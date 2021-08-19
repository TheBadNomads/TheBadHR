import discord
import os

from collections import defaultdict
from datetime import date, timedelta, datetime
from discord_slash.utils.manage_commands import create_option, create_choice

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

async def UpdateEmbedLeaveStatus(message, embed, newStatus):
    embed_dict = embed.to_dict()

    for field in embed_dict["fields"]:
        if field["name"].lower() == "status":
            field["value"] = newStatus

    embed = discord.Embed.from_dict(embed_dict)

    await message.edit(embed=embed)

def ParseEmoji(emoji):
    emoji_str = str(emoji)
    reaction_emojis = {
        os.getenv("Approve_Emoji"): "Approved",
        os.getenv("Reject_Emoji"): "Rejected"
    }
    reaction_emojis_dict = defaultdict("", **reaction_emojis)

    return reaction_emojis_dict[emoji_str]

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