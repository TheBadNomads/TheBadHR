import discord
import os

from db import db
from collections import defaultdict
from datetime import date, timedelta, datetime
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option, create_choice
from Leave import leave_db

def CreateLeaveEmbed(ctx, startdate, enddate, leaveType):
    leaveImages = {
        "Annual"   : os.getenv("Annual_Leave_Link"),
        "Emergency": os.getenv("Emergency_Leave_Link"),
        "Sick"     : os.getenv("Sick_Leave_Link")
    }

    embed = discord.Embed(
        title = f'{leaveType} Leave Request', 
        description = f'{ctx.author.mention} is requesting '+ leaveType.lower() +' leave', 
        colour = 0x4682B4
    )

    embed.set_thumbnail(url = leaveImages[leaveType])
    embed.add_field(name = "Start Date", value = startdate, inline = True)
    embed.add_field(name = "End Date", value = enddate, inline = True)
    embed.add_field(name = '\u200B', value = '\u200B', inline = False)
    embed.add_field(name = "Status", value = "Pending", inline = False)
    embed.set_footer(text = date.today())

    return embed
    
def CreateLeaveTypeChoices():
    leaveTypeChoices = []
    for leaveType in leave_db.GetLeaveTypesWithBalance():
        leaveTypeChoices.append(create_choice(name = leaveType["name"], value = leaveType["name"]))

    return leaveTypeChoices

def CreateDateChoices():
    current_hour = datetime.datetime.now().time()
    end_of_core = datetime.time(13)
    firstDate = date.today()
    dateChoices = []
   
    if current_hour >= end_of_core:
        firstDate = date.today() + timedelta(1)

    for i in range(25):
        tmpDate = firstDate + timedelta(i)
        weekDay = tmpDate.strftime("%A")
        dateChoices.append(create_choice(name = weekDay +": "+ tmpDate.strftime('%d/%m/%Y'), value = tmpDate.strftime('%d/%m/%Y')))
    
    return dateChoices

def CreateDateOptions():
    requestLeave_options = [
        create_option(
            name = "leavetype",
            description = "leave type",
            option_type = SlashCommandOptionType.STRING,
            required = True,
            choices = CreateLeaveTypeChoices()
        ),
        create_option(
            name = "startdate",
            description = "starting date of your leave",
            option_type = SlashCommandOptionType.STRING,
            required = True,
            choices = CreateDateChoices()
        ),
        create_option(
            name = "enddate",
            description = "Leave empty for 1 day leave",
            option_type = SlashCommandOptionType.STRING,
            required = True,
            choices = CreateDateChoices()
        ),
        create_option(
            name = "reason",
            description = "reason for the leave (optional)",
            option_type = SlashCommandOptionType.STRING,
            required = False
        )
    ]

    return requestLeave_options

def CreateMemberOptions():
    member_options = [
        create_option(
            name = "discorduser",
            description = "discord user",
            option_type = SlashCommandOptionType.USER,
            required = True
        ),
        create_option(
            name = "name",
            description = "name",
            option_type = SlashCommandOptionType.STRING,
            required = True
        ),
        create_option(
            name = "email",
            description = "email",
            option_type = SlashCommandOptionType.STRING,
            required = True
        ),
        create_option(
            name = "startdate",
            description = "working start date format: DD/MM/YYYY",
            option_type = SlashCommandOptionType.STRING,
            required = True
        )
    ]

    return member_options

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
    reaction_emojis = defaultdict(None, **reaction_emojis)

    return reaction_emojis[emoji_str]