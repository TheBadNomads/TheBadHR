import os
import datetime
import Utilities as utils
import calendar
import hikari
import lightbulb

from db import db
from lightbulb.commands.base import OptionLike
from hikari.commands import CommandChoice
from hikari.impl import EntityFactoryImpl
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from Leave import leave_db
from Member import member_db

embed_footer_spaces_count = 150

def CreateLeaveEmbed(ctx, start_date, end_date, leave_type, reason):
	leaveImages = {
		"Annual": os.getenv("Annual_Leave_Link")
		, "Sick": os.getenv("Sick_Leave_Link")
	}

	embed = hikari.Embed(
		title = "Leave Request"
		, description = f"{ctx.author.mention} is requesting a leave"
		, color = 0x4682B4
	)

	if not reason:
		reason = "None"

	footer_text = (("\u2008" * embed_footer_spaces_count) + datetime.date.today().strftime("%Y-%m-%d"))

	embed.set_thumbnail(leaveImages[leave_type])
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
		leaveTypeChoices.append(leaveType["name"])

	return leaveTypeChoices

def CreateDateChoices():
	current_hour = datetime.datetime.now().time()
	end_of_core = datetime.time(13)
	firstDate = datetime.date.today()
	date_choices = []

	if current_hour >= end_of_core:
		firstDate = datetime.date.today() + datetime.timedelta(1)

	for i in range(25):
		tmpDate = firstDate + datetime.timedelta(i)
		weekDay = tmpDate.strftime("%A")
		date_choices.append(CommandChoice(name = weekDay + ": "+ tmpDate.strftime("%Y-%m-%d"), value = tmpDate.strftime("%Y-%m-%d")))
	
	return date_choices

def CreateMonthChoices():
	month_choices = []
	for index in range(1, 13):
		month_choices.append(CommandChoice(name = calendar.month_name[index], value = index))

	return month_choices

def CreateYearChoices():
	year_choices = []
	max_range = (datetime.datetime.now().year - int(os.getenv("Company_Starting_Year"))) + 1
	for index in range(0, max_range):
		value = int(os.getenv("Company_Starting_Year")) + index
		year_choices.append(value)

	return year_choices

def CreateLeaveRequestOptions():
	requestLeave_options = {
		"leavetype": OptionLike(name = "leavetype", description = "leave type", arg_type = str, required = True, choices = CreateLeaveTypeChoices())
		, "startdate": OptionLike(name = "startdate", description = "starting date of your leave", arg_type = str, required = True, choices = CreateDateChoices())
		, "enddate": OptionLike(name = "enddate", description = "ending date of your leave", arg_type = str, required = True, choices = CreateDateChoices())
		, "reason": OptionLike(name = "reason", description = "reason for the leave (optional)", arg_type = str, required = False, default = "")
	}
	
	return requestLeave_options

def CreateMemberInsertionOptions():
	member_options = {
		"discorduser": OptionLike(name = "discorduser", description = "discord user", arg_type = hikari.User, required = True)
		, "name": OptionLike(name = "name", description = "name", arg_type = str, required = True)
		, "email": OptionLike(name = "email", description = "email", arg_type = str, required = True)
		, "startdate": OptionLike(name = "startdate", description = "working start date format: YYYY-MM-DD", arg_type = str, required = True)
	}

	return member_options

def CreateRetroactiveLeaveInsertionOptions():
	retroactive_application_options = {
		"discorduser": OptionLike(name = "discorduser", description = "discord user", arg_type = hikari.User, required = True)
		, "leavetype": OptionLike(name = "leavetype", description = "leavetype", arg_type = "class <'str'>", required = True, choices = CreateLeaveTypeChoices())
		, "startdate": OptionLike(name = "startdate", description = "starting date of the leave in YYYY-MM-DD format", arg_type = str, required = True)
		, "enddate": OptionLike(name = "enddate", description = "ending date of the leave in YYYY-MM-DD format", arg_type = str, required = True)
		, "isemergency": OptionLike(name = "isemergency", description = "determines if the user requested the retroactive leave late", arg_type = bool, required = True)
		, "isunpaid": OptionLike(name = "isunpaid", description = "determines if the leave is considered unpaid", arg_type = bool, required = True)
		, "reason": OptionLike(name = "reason", description = "reason for the leave (optional)", arg_type = str, required = False, default = "")
	}

	return retroactive_application_options

def CreateLeavesBalancesEmbed(member, author_id = None):
	if(author_id == member.id or author_id == None):
		description_text = "Your balances are:"
	else:
		description_text = f"{member.username}'s balances are:"

	embed = hikari.Embed(
		title = f'Leave Balances'
		, description = description_text
		, colour = 0x4682B4
	)

	embed.set_thumbnail(os.getenv("Leave_Balance_Image"))
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
	"Annual": os.getenv("Annual_Leave_Link")
	, "Sick": os.getenv("Sick_Leave_Link")
	}

	embed = hikari.Embed(
		title = f'Leave Request Status'
		, description = f'Request ID: ' + str(request_id)
		, colour = 0x4682B4
	)
	if reason == "":
		reason = "None"
		
	footer_text = (("\u200B " * embed_footer_spaces_count) + datetime.date.today().strftime("%Y-%m-%d"))

	embed.set_thumbnail(leaveImages[leave_type])
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
	embed = hikari.Embed(
		title = f"{member.username}'s Information",
		description = "",
		colour = 0x4682B4
	)

	if(member_db_info["leave_date"]):
		leave_date = (member_db_info["leave_date"]).strftime('%Y-%m-%d')
	else:
		leave_date = "Still Employed"
	
	embed.add_field(name = "Full Name", value = member_db_info["name"], inline = True)
	embed.add_field(name = "Email", value = member_db_info["email"], inline = True)
	embed.add_field(name = "Roles", value = " - ".join([role.name for role in member.get_roles()[1:]]), inline = False)
	embed.add_field(name = "Start Date", value = (member_db_info["start_date"]).strftime('%Y-%m-%d'), inline = True)
	embed.add_field(name = "Leave Date", value =  leave_date, inline = True)
	embed.add_field(name = "Starting Leaves Balance", value =  member_db.CalculateProratedAnnualLeaves(member.id), inline = False)

	footer_text = (("\u200B " * embed_footer_spaces_count) + datetime.date.today().strftime("%Y-%m-%d"))
	embed.set_footer(text = footer_text)

	return embed

def CreateIsMemberWorkingOptions():
	member_options = {
		"discorduser": OptionLike(name = "discorduser", description = "discord user", arg_type = hikari.User, required = True)
		, "date": OptionLike(name = "date", description = "date of interest(optional) leave empty for today", arg_type = str, required = False, choices = CreateDateChoices(), default = datetime.datetime.today().strftime('%Y-%m-%d'))
	}

	return member_options

def CreateIsEveryoneHereEmbed(approved_dict, missing_members, isAdmin):
	embed = hikari.Embed(
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
	end_of_month_Report_options = {
		"members": OptionLike(name = "members", description = "@Member1 @Member2... (optional) leave empty for all members", arg_type = str, required = False, default = "")
		, "month": OptionLike(name = "month", description = "(optional) leave empty for current month", arg_type = int, required = False, choices = CreateMonthChoices(), default = None)
		, "year": OptionLike(name = "year", description = "(optional) leave empty for current year", arg_type = int, required = False, choices = CreateYearChoices(), default = None)
	}

	return end_of_month_Report_options

def CreateGetEndOfYearReportOptions():
	end_of_year_Report_options = {
		"members": OptionLike(name = "members", description = "@Member1 @Member2... (optional) leave empty for all members", arg_type = str, required = False, default = "")
		, "year": OptionLike(name = "year", description = "(optional) leave empty for current year", arg_type = int, required = False, choices = CreateYearChoices(), default = None)
	}

	return end_of_year_Report_options
	
def CreateGetEndOfMonthReportEmbed(members_list, month = None, year = None):
	month = month or datetime.datetime.now().month
	year = year or datetime.datetime.now().year
	embed = hikari.Embed(
		title = f'End of Month Report',
		description = f'{year}-{month} Report:',
		colour = 0x4682B4
	)
	embed.set_thumbnail(os.getenv("Salary_Image"))
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
	embed = hikari.Embed(
		title = f'End of Year Report',
		description = f'{year} Report:',
		colour = 0x4682B4
	)
	embed.set_thumbnail(os.getenv("Salary_Image"))
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

async def UpdateLeaveEmbed(client, member, embed, newStatus, channel, message, token):
	await UpdateEmbedLeaveStatus(client, embed, newStatus, channel, message, token)
	await UpdateEmbedApprovedRejectedby(client, member, embed, channel, message, token)

def CreateCreditLeavesOptions():
	extra_balance_options = {
		"discorduser": OptionLike(name = "discorduser", description = "discord user", arg_type = hikari.User, required = True)
		, "leavetype": OptionLike(name = "leavetype", description = "leave type", arg_type = str, required = True, choices = CreateLeaveTypeChoices())
		, "dayscount": OptionLike(name = "dayscount", description = "amount of extra leaves to credit (can be a negative number). Defaults to 1", arg_type = float, required = False, default = 1)
		, "reason": OptionLike(name = "reason", description = "reason behind the extra balance (optional)", arg_type = str, required = False, default = "")
	}

	return extra_balance_options

def CreateGetLeavesAcrossRangeOptions():
	get_leaves_across_range_options = {
		"startdate": OptionLike(name = "startdate", description = "start date (inclusive) in YYYY-MM-DD format", arg_type = str, required = True)
		, "enddate": OptionLike(name = "enddate", description = "end date (inclusive) in YYYY-MM-DD format", arg_type = str, required = True)
		, "discorduser": OptionLike(name = "discorduser", description = "discord user (optional) leaving this empty will query for everyone", arg_type = hikari.User, required = False, default = None)
	}

	return get_leaves_across_range_options

def CreateLeavesAcrossRangeEmbed(leaves, startdate, enddate, include_reason):
	embed = hikari.Embed(
		title = f'Applied Leaves',
		description = f'Dates range: \u200B \u200B**{startdate}** \u200B \u200B \u200B \u200B - \u200B \u200B \u200B \u200B **{enddate}**',
		colour = 0x4682B4
	)
	embed.set_thumbnail(os.getenv("Leave_Balance_Image"))
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

async def UpdateEmbedLeaveStatus(client, embed, newStatus, channel, message, token):
	embed_tuple = client.entity_factory.serialize_embed(embed = embed)

	for field in embed_tuple[0]["fields"]:
		if field["name"].lower() == "status":
			field["value"] = newStatus

	embed = client.entity_factory.deserialize_embed(embed_tuple[0])

	async with hikari.RESTApp().acquire(token, hikari.TokenType.BOT) as client:
		message = await client.fetch_message(channel, message)
		await client.edit_message(message = message, embed = embed, channel = channel)

async def UpdateEmbedApprovedRejectedby(client, member, embed, channel, message, token):
	embed_tuple = client.entity_factory.serialize_embed(embed = embed)

	for field in embed_tuple[0]["fields"]:
		if field["name"].lower() == "approved/rejected by":
			field["value"] = f'<@!{member.id}>'

	embed = client.entity_factory.deserialize_embed(embed_tuple[0])

	async with hikari.RESTApp().acquire(token, hikari.TokenType.BOT) as client:
		message = await client.fetch_message(channel, message)
		await client.edit_message(message = message, embed = embed, channel = channel)

def ParseEmoji(emoji):
	emoji_str = str(emoji)
	reaction_emojis = {
		os.getenv("Approve_Emoji_ID"): "Approved",
		os.getenv("Reject_Emoji_ID"): "Rejected",
		os.getenv("Revert_Emoji_ID"): "Reverted"
	}
	reaction_emojis = defaultdict(None, **reaction_emojis)

	return reaction_emojis[emoji_str]
