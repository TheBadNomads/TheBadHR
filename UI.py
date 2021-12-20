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
        "Sick"     : os.getenv("Sick_Leave_Link"),
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
    embed.add_field(name = "Status", value = "Pending", inline = True)
    embed.add_field(name = "Approved/Rejected by", value = "None", inline = True)
    embed.set_footer(text = footer_text)
    return embed
    
def CreateLeaveTypeChoices():
    leaveTypeChoices = []
    for leaveType in leave_db.GetLeaveTypes():
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

def CreateLeaveRequestOptions():
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
            description = "ending date of your leave",
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

def CreateMemberInsertionOptions():
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

def CreateRetroactiveLeaveInsertionOptions():
    retroactive_application_options = [
        create_option(
            name = "discorduser",
            description = "discord user",
            option_type = SlashCommandOptionType.USER,
            required = True
        ),
        create_option(
            name = "leavetype",
            description = "leave type",
            option_type = SlashCommandOptionType.STRING,
            required = True,
            choices = CreateLeaveTypeChoices()
        ),
         create_option(
            name = "startdate",
            description = "starting date of the leave in DD/MM/YYYY format",
            option_type = SlashCommandOptionType.STRING,
            required = True
        ),
        create_option(
            name = "enddate",
            description = "ending date of the leave in DD/MM/YYYY format",
            option_type = SlashCommandOptionType.STRING,
            required = True
        ),
        create_option(
            name = "isemergency",
            description = "determines if the user requested the retroactive leave late",
            option_type = SlashCommandOptionType.BOOLEAN,
            required = True
        ),
        create_option(
            name = "isunpaid",
            description = "determines if the leave is considered unpaid",
            option_type = SlashCommandOptionType.BOOLEAN,
            required = True
        ),
        create_option(
            name = "reason",
            description = "reason for the leave (optional)",
            option_type = SlashCommandOptionType.STRING,
            required = False
        )
    ]
    return retroactive_application_options

def CreateLeavesBalancesEmbed(member_id):
    try:
        embed = discord.Embed(
            title = f'Leave Balances',
            description = f'Your balances are:',
            colour = 0x4682B4
        )
        embed.set_thumbnail(url = os.getenv("Leave_Balance_Link"))
        embed.add_field(name = '\u200B', value = '\u200B', inline = False)

        embed.add_field(name = "Annual", value = leave_db.GetAnnualLeaveBalance(member_id), inline = True)
        embed.add_field(name = '\u200B', value = '\u200B', inline = True)
        embed.add_field(name = "Emergency", value = max(GetEmergencyBalance(member_id), 0), inline = True)

        embed.add_field(name = '\u200B', value = '\u200B', inline = False)
        embed.set_footer(text = datetime.date.today())
        return embed

    except Exception as e:
        print(e)
        return None

def CreateIsMemberWorkingOptions():
    member_options = [
        create_option(
            name = "discorduser",
            description = "discord user",
            option_type = SlashCommandOptionType.USER,
            required = True
        ),
        create_option(
            name = "date",
            description = "date of interest (optional) leave empty for today",
            option_type = SlashCommandOptionType.STRING,
            required = False,
            choices = CreateDateChoices()
        )
    ]

    return member_options
    
async def UpdateLeaveEmbed(member, message, embed, newStatus):
    await UpdateEmbedLeaveStatus(message, embed, newStatus)
    await UpdateEmbedApprovedRejectedby(message, embed, member)

def CreateCreditLeavesOptions():
    ApplicationCommandOptionType_FLOAT = 10
    extra_balance_options = [
        create_option(
            name = "discorduser",
            description = "discord user",
            option_type = SlashCommandOptionType.USER,
            required = True
        ),
        create_option(
            name = "leavetype",
            description = "leave type",
            option_type = SlashCommandOptionType.STRING,
            required = True,
            choices = CreateLeaveTypeChoices()
        ),
        create_option(
            name = "dayscount",
            description = "amount of extra leaves to credit (can be a negative number). Defaults to 1",
            option_type = ApplicationCommandOptionType_FLOAT,
            required = False
        ),
        create_option(
            name = "reason",
            description = "reason behind the extra balance (optional)",
            option_type = SlashCommandOptionType.STRING,
            required = False
        )
    ]

    return extra_balance_options

async def UpdateEmbedLeaveStatus(message, embed, newStatus):
    embed_dict = embed.to_dict()

    for field in embed_dict["fields"]:
        if field["name"].lower() == "status":
            field["value"] = newStatus

    embed = discord.Embed.from_dict(embed_dict)

    await message.edit(embed=embed)

async def UpdateEmbedApprovedRejectedby(message, embed, member):
    embed_dict = embed.to_dict()

    for field in embed_dict["fields"]:
        if field["name"].lower() == "approved/rejected by":
            field["value"] = f'<@!{member.id}>'

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

def GetEmergencyBalance(member_id):
    requested_emergency_count = len(leave_db.GetEmergencyLeavesForYear(member_id, datetime.date.today().year))
    max_emergency_count = int(os.getenv("Emergency_Leaves_Max_Count"))
    return (max_emergency_count - requested_emergency_count)
