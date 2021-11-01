import discord
import os
import datetime
import Utilities as utils

from db import db
from collections import defaultdict
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option, create_choice
from Leave import leave_db

def CreateLeaveEmbed(ctx, start_date, end_date, leave_type, reason):
    leaveImages = {
        "Annual"   : os.getenv("Annual_Leave_Link"),
        "Emergency": os.getenv("Emergency_Leave_Link"),
        "Sick"     : os.getenv("Sick_Leave_Link"),
        "Unpaid"   : os.getenv("Unpaid_Leave_Link")
    }
    embed = discord.Embed(
        title = 'Leave Request', 
        description = f'{ctx.author.mention} is requesting a leave', 
        colour = 0x4682B4
    )
    if reason == "":
        reason = "None"
    footer_text = (("\u200B " * 150) + datetime.date.today().strftime("%d/%m/%Y")) # magic number 150

    embed.set_thumbnail(url = leaveImages[leave_type])
    embed.add_field(name = "Leave Type", value = leave_type, inline = False)
    embed.add_field(name = "Start Date", value = start_date.date(), inline = True)
    embed.add_field(name = "End Date", value = end_date.date(), inline = True)
    embed.add_field(name = "No. of Days", value = len(utils.GetWorkDays(start_date, end_date)), inline = True)
    embed.add_field(name = "Reason", value = reason, inline = False)
    embed.add_field(name = "Status", value = "Pending", inline = False)
    embed.set_footer(text = footer_text)
    return embed
    
def CreateLeaveTypeChoices():
    leaveTypeChoices = []
    for leaveType in leave_db.GetLeaveTypesWithBalance():
        leaveTypeChoices.append(create_choice(name = leaveType["name"], value = leaveType["name"]))

    return leaveTypeChoices

def CreateDateChoices():
    current_hour = datetime.datetime.now().time()
    end_of_core = datetime.time(13)
    firstDate = datetime.date.today()
    dateChoices = []
   
    if current_hour >= end_of_core:
        firstDate = datetime.date.today() + datetime.timedelta(1)

    for i in range(25):
        tmpDate = firstDate + datetime.timedelta(i)
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