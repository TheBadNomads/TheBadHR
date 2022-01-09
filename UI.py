import discord
import os
import datetime
import Utilities as utils
import calendar

from db import db
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option, create_choice
from Leave import leave_db
from Member import member_db

embed_footer_spaces_count = 150

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
    footer_text = (("\u200B " * embed_footer_spaces_count) + datetime.date.today().strftime("%Y-%m-%d"))

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
        dateChoices.append(create_choice(name = weekDay +": "+ tmpDate.strftime('%Y-%m-%d'), value = tmpDate.strftime('%Y-%m-%d')))
    
    return dateChoices

def CreateMonthChoices():
    month_choices = []
    for index in range(1, 13):
        month_choices.append(create_choice(name = calendar.month_name[index], value = index))

    return month_choices

def CreateYearChoices():
    year_choices = []
    max_range = (datetime.datetime.now().year - int(os.getenv("Company_Starting_Year"))) + 1
    for index in range(0, max_range):
        value = int(os.getenv("Company_Starting_Year")) + index
        year_choices.append(create_choice(name = value, value = value))

    return year_choices

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
            description = "working start date format: YYYY-MM-DD",
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
            description = "starting date of the leave in YYYY-MM-DD format",
            option_type = SlashCommandOptionType.STRING,
            required = True
        ),
        create_option(
            name = "enddate",
            description = "ending date of the leave in YYYY-MM-DD format",
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

def CreateLeavesBalancesEmbed(member, author_id = None):
    if(author_id == member.id or author_id == None):
        description_text = "Your balances are:"
    else:
        description_text = f"{member.display_name}'s balances are:"
    embed = discord.Embed(
        title = f'Leave Balances',
        description = description_text,
        colour = 0x4682B4
    )
    embed.set_thumbnail(url = os.getenv("Leave_Balance_Image"))
    embed.add_field(name = '\u200B', value = '\u200B', inline = False)

    embed.add_field(name = "Annual", value = leave_db.GetAnnualLeaveBalance(member.id), inline = True)
    embed.add_field(name = '\u200B', value = '\u200B', inline = True)
    embed.add_field(name = "Emergency", value = max(leave_db.GetRemainingEmergencyLeavesCount(member.id), 0), inline = True)

    embed.add_field(name = '\u200B', value = '\u200B', inline = False)
    footer_text = (("\u200B " * embed_footer_spaces_count) + datetime.date.today().strftime("%Y-%m-%d"))
    embed.set_footer(text = footer_text)
    return embed

def CreateInformMemberOfLeaveStatusEmbed(request_id, status, admin_name, reason, leave_type, start_date, end_date):
    leaveImages = {
    "Annual"   : os.getenv("Annual_Leave_Link"),
    "Sick"     : os.getenv("Sick_Leave_Link"),
    }
    embed = discord.Embed(
        title = f'Leave Request Status',
        description = f'Request ID: ' + str(request_id),
        colour = 0x4682B4
    )
    if reason == "":
        reason = "None"
        
    footer_text = (("\u200B " * embed_footer_spaces_count) + datetime.date.today().strftime("%Y-%m-%d"))

    embed.set_thumbnail(url = leaveImages[leave_type])
    embed.add_field(name = "Leave Type", value = leave_type, inline = False)
    embed.add_field(name = "Start Date", value = start_date.date(), inline = True)
    embed.add_field(name = "End Date", value = end_date.date(), inline = True)
    embed.add_field(name = "No. of Days", value = len(utils.GetWorkDays(start_date, end_date)), inline = True)
    embed.add_field(name = "Reason", value = reason, inline = False)
    embed.add_field(name = "Status", value = status, inline = True)
    embed.add_field(name = "Approved/Rejected by", value = admin_name, inline = True)
    embed.set_footer(text = footer_text)
    
    return embed

def CreateMemberInfoEmbed(member, member_db_info):
    embed = discord.Embed(
        title = f"{member.display_name}'s Information",
        description = "",
        colour = 0x4682B4
    )

    if(member_db_info["leave_date"]):
        leave_date = (member_db_info["leave_date"]).strftime('%Y-%m-%d')
    else:
        leave_date = "Still Employed"
    
    embed.add_field(name = "Full Name", value = member_db_info["name"], inline = True)
    embed.add_field(name = "Email", value = member_db_info["email"], inline = True)
    embed.add_field(name = "Roles", value = " - ".join([role.name for role in member.roles[1:]]), inline = False)
    embed.add_field(name = "Start Date", value = (member_db_info["start_date"]).strftime('%Y-%m-%d'), inline = True)
    embed.add_field(name = "Leave Date", value =  leave_date, inline = True)
    embed.add_field(name = "Starting Leaves Balance", value =  member_db.CalculateProratedAnnualLeaves(member.id), inline = False)

    footer_text = (("\u200B " * embed_footer_spaces_count) + datetime.date.today().strftime("%Y-%m-%d"))
    embed.set_footer(text = footer_text)

    return embed

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

def CreateIsEveryoneHereEmbed(approved_dict, missing_members, isAdmin):
    
    embed = discord.Embed(
        title = f'Is Everyone Here',
        description = f'Members not in meeting channel',
        colour = 0x4682B4
    )
    
    if missing_members:
        embed.add_field(name = "Names", value = '\n'.join(missing_members), inline = False)
    else:
        embed.add_field(name = "Everyone's Here", value = "-", inline = False)

    if approved_dict:
        embed.add_field(name = "Approved Leaves", value = '\n'.join(approved_dict.keys()), inline = True)
        if isAdmin:
            approved_reasons = [reason if reason != "" else "None" for reason in approved_dict.values()]
            embed.add_field(name = "Reasons", value = '\n'.join(approved_reasons), inline = True)

    footer_text = (("\u200B " * embed_footer_spaces_count) + datetime.date.today().strftime("%Y-%m-%d"))
    embed.set_footer(text = footer_text)
    return embed

def CreateGetEndOfMonthReportOptions():
    end_of_month_Report_options = [
        create_option(
            name = "members",
            description = "@Member1 @Member2... (optional) leave empty for all members",
            option_type = SlashCommandOptionType.STRING,
            required = False
        ),
        create_option(
            name = "month",
            description = "(optional) leave empty for current month",
            option_type = SlashCommandOptionType.INTEGER,
            required = False,
            choices = CreateMonthChoices()
        ),
        create_option(
            name = "year",
            description = "(optional) leave empty for current year",
            option_type = SlashCommandOptionType.INTEGER,
            required = False,
            choices = CreateYearChoices()
        )
    ]

    return end_of_month_Report_options

def CreateGetEndOfYearReportOptions():
    end_of_year_Report_options = [
        create_option(
            name = "members",
            description = "@Member1 @Member2... (optional) leave empty for all members",
            option_type = SlashCommandOptionType.STRING,
            required = False
        ),
        create_option(
            name = "year",
            description = "(optional) leave empty for current year",
            option_type = SlashCommandOptionType.INTEGER,
            required = False,
            choices = CreateYearChoices()
        )
    ]

    return end_of_year_Report_options
    
def CreateGetEndOfMonthReportEmbed(members_list, month = None, year = None):
    month = month or datetime.datetime.now().month
    year = year or datetime.datetime.now().year
    embed = discord.Embed(
        title = f'End of Month Report',
        description = f'{year}-{month} Report:',
        colour = 0x4682B4
    )
    embed.set_thumbnail(url = os.getenv("Salary_Image"))
    embed.add_field(name = '\u200B', value = '\u200B', inline = False)

    for member in members_list:
        member_data = FormatGetEndOfMonthReportEmbed(member, month, year)
        embed.add_field(name = f'**{member["name"].upper()}**', value = member_data, inline = False)
        embed.add_field(name = '\u200B', value = '\u200B', inline = False)

    footer_text = (("\u200B " * embed_footer_spaces_count) + datetime.date.today().strftime("%Y-%m-%d"))
    embed.set_footer(text = footer_text)
    return embed

def FormatGetEndOfMonthReportEmbed(member, month, year):
    member_data = ""
    start_date = datetime.datetime(year, month, int(os.getenv("End_of_Month_Report_Day"))) - relativedelta(months = 1)
    end_date = datetime.datetime(year, month, int(os.getenv("End_of_Month_Report_Day"))) - datetime.timedelta(days = 1)
    
    paid_leaves = leave_db.GetApprovedPaidLeaves(member["id"], start_date, end_date)
    unpaid_leaves = leave_db.GetApprovedUnpaidLeaves(member["id"], start_date, end_date)
    sick_leaves = leave_db.GetApprovedSickLeaves(member["id"], start_date, end_date)
    emergency_leaves = leave_db.GetApprovedEmergencyLeaves(member["id"], start_date, end_date)
    deduction_precentage_of_unpaid = utils.CalculatePercentage(len(unpaid_leaves), float(os.getenv("Average_Working_Days_Count")))

    member_data += f' \u200B \u200B ***Paid Leaves Taken:*** \u200B \u200B{len(paid_leaves)} \u200B \u200B ***Sick:*** {len(sick_leaves)} \u200B \u200B ***Emergency:*** {len(emergency_leaves)}\n'
    member_data += f' \u200B \u200B ***Unpaid Leaves Taken:*** \u200B \u200B{len(unpaid_leaves)}\n'
    member_data += f' \u200B \u200B ***Unpaid Deduction Percentage:*** \u200B \u200B{deduction_precentage_of_unpaid}%\n'
        
    return member_data

def CreateGetEndOfYearReportEmbed(members_list, year = None):
    year = year or datetime.datetime.now().year
    embed = discord.Embed(
        title = f'End of Year Report',
        description = f'{year} Report:',
        colour = 0x4682B4
    )
    embed.set_thumbnail(url = os.getenv("Salary_Image"))
    embed.add_field(name = '\u200B', value = '\u200B', inline = False)

    for member in members_list:
        member_data = FormatGetEndOfYearReportEmbed(member, year)
        embed.add_field(name = f'**{member["name"].upper()}**', value = member_data, inline = False)
        embed.add_field(name = '\u200B', value = '\u200B', inline = False)

    footer_text = (("\u200B " * embed_footer_spaces_count) + datetime.date.today().strftime("%Y-%m-%d"))
    embed.set_footer(text = footer_text)
    return embed

def FormatGetEndOfYearReportEmbed(member, year):
    member_data = ""
    start_date = datetime.datetime(year - 1, 12, int(os.getenv("End_of_Year_Report_Day")))
    end_date = start_date + relativedelta(years = 1)
    paid_leaves = leave_db.GetApprovedPaidLeaves(member["id"], start_date, end_date)
    sick_leaves = leave_db.GetApprovedSickLeaves(member["id"], start_date, end_date)
    emergency_leaves = leave_db.GetApprovedEmergencyLeaves(member["id"], start_date, end_date)
    remaining_leaves_balance = leave_db.GetAnnualLeaveBalance(member["id"])
    bonus_precentage = utils.CalculatePercentage(remaining_leaves_balance, float(os.getenv("Average_Working_Days_Count")))

    member_data += f' \u200B \u200B ***Yearly Paid Leaves Taken:*** \u200B \u200B{len(paid_leaves)} \u200B \u200B ***Sick:*** {len(sick_leaves)} \u200B \u200B ***Emergency:*** {len(emergency_leaves)}\n'
    member_data += f' \u200B \u200B ***Remaining Leaves Balance:*** \u200B \u200B{remaining_leaves_balance}\n'
    member_data += f' \u200B \u200B ***Bonus Percentage:*** \u200B \u200B{bonus_precentage}%\n'

    return member_data

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

def CreateGetLeavesAcrossRangeOptions():
    get_leaves_across_range_options = [
        create_option(
            name = "startdate",
            description = "start date (inclusive) in YYYY-MM-DD format",
            option_type = SlashCommandOptionType.STRING,
            required = True
        ),
        create_option(
            name = "enddate",
            description = "end date (inclusive) in YYYY-MM-DD format",
            option_type = SlashCommandOptionType.STRING,
            required = True
        ),
        create_option(
            name = "discorduser",
            description = "discord user (optional) leaving this empty will query for everyone",
            option_type = SlashCommandOptionType.USER,
            required = False
        )
    ]

    return get_leaves_across_range_options

def CreateLeavesAcrossRangeEmbed(leaves, startdate, enddate, include_reason):
    embed = discord.Embed(
        title = f'Applied Leaves',
        description = f'Dates range: \u200B \u200B**{startdate}** \u200B \u200B \u200B \u200B - \u200B \u200B \u200B \u200B **{enddate}**',
        colour = 0x4682B4
    )
    embed.set_thumbnail(url = os.getenv("Leave_Balance_Image"))
    embed.add_field(name = '\u200B', value = '\u200B', inline = False)

    for leaves_group in leaves:
        leaves_value = FormatLeavesAcrossRangeEmbed(leaves_group, include_reason)
        if leaves_value == "":
            continue
        member_name = member_db.GetMemberByID(leaves_group[0][0]["member_id"])["name"]
        embed.add_field(name = f'**{member_name.upper()}**', value = leaves_value, inline = False)
        embed.add_field(name = '\u200B', value = '\u200B', inline = False)

    footer_text = (("\u200B " * embed_footer_spaces_count) + datetime.date.today().strftime("%Y-%m-%d"))
    embed.set_footer(text = footer_text)
    return embed

def FormatLeavesAcrossRangeEmbed(leaves_group, include_reason):
    leaves_value = ""
    for leaves_array in leaves_group:
        if (leaves_array[0]["leave_status"] != "Approved" and (not (include_reason))):
            continue
        leaves_value += f' \u200B \u200B ***Type:*** \u200B \u200B{leaves_array[0]["leave_type"]}\n'
        leaves_value += f' \u200B \u200B ***From:*** \u200B \u200B{leaves_array[0]["date"].strftime("%Y-%m-%d")}  \u200B \u200B \u200B \u200B \u200B ***To:*** \u200B \u200B{leaves_array[-1]["date"].strftime("%Y-%m-%d")}\n'
        if include_reason:
            reason = leaves_array[0]["reason"]
            leaves_value += f' \u200B \u200B ***Reason:*** \u200B \u200B{reason or "None"}\n'
            leaves_value += f' \u200B \u200B ***Status:*** \u200B \u200B{leaves_array[0]["leave_status"]}\n'
        leaves_value += '\n'
    return leaves_value

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
        os.getenv("Reject_Emoji"): "Rejected",
        os.getenv("Revert_Emoji"): "Reverted"
    }
    reaction_emojis = defaultdict(None, **reaction_emojis)

    return reaction_emojis[emoji_str]
