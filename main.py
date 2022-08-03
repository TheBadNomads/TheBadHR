import datetime
import hikari
import lightbulb
import os
import Utilities
import Scheduler
import UI

from db import db
from dotenv import load_dotenv
from Member import member_db
from Leave import leave_interface, leave_db

load_dotenv()

bot = lightbulb.BotApp(token = os.getenv("Bot_token"), intents = hikari.Intents.ALL)

guild_ids = [int(os.getenv("TestServer_id"))]
deletion_timer = float(os.getenv("Command_Deletion_Timer"))

@bot.listen(lightbulb.events.LightbulbStartedEvent)
async def on_ready(event: lightbulb.events.LightbulbStartedEvent):
	Scheduler.Setup(bot)
	print("Bot is ready.")

@bot.listen(hikari.GuildReactionAddEvent)
async def on_reaction_add(event: hikari.GuildReactionAddEvent):
	await leave_interface.HandleLeaveReactions(bot, event, os.getenv("Bot_token"))

@bot.command
@lightbulb.command(name = "requestleave", description = "Requests an annual leave", guilds = guild_ids)
@lightbulb.implements(lightbulb.SlashCommand)
async def RequestLeave(ctx):
	message_content = await leave_interface.ProcessLeaveRequest(ctx, ctx.author, bot, ctx.options.leavetype, datetime.datetime.strptime(ctx.options.startdate, "%Y-%m-%d"), datetime.datetime.strptime(ctx.options.enddate, "%Y-%m-%d"), ctx.options.reason)
	await ctx.author.send(content = message_content)
	await ctx.respond(content = "Done", delete_after = deletion_timer)

@bot.command
@lightbulb.command(name = "insertmember", description = "Inserts a new member into the database", guilds = guild_ids)
@lightbulb.implements(lightbulb.SlashCommand)
async def InsertMember(ctx):
	author = ctx.get_guild().get_member(ctx.author)

	if Utilities.IsAdmin(author) or Utilities.IsBotManager(author):
		member_db.InsertMember(ctx.options.discorduser.id, ctx.options.name, ctx.options.email, datetime.datetime.strptime(ctx.options.startdate, "%Y-%m-%d"))
		member_db_info = member_db.GetMemberByID(ctx.options.discorduser.id)
		embed = UI.CreateMemberInfoEmbed(ctx.options.discorduser, member_db_info)
		await ctx.author.send(embed = embed)

	else:
		await ctx.author.send(content = "This command is for Admins only")

	await ctx.respond(content = "Done", delete_after = deletion_timer)

@bot.command
@lightbulb.command(name = "insertretroactiveleave", description = "Inserts a late leave (Admins Only)", guilds = guild_ids)
@lightbulb.implements(lightbulb.SlashCommand)
async def InsertRetroactiveLeave(ctx):
	reply = await ctx.respond(content = "Processing")
	msg = await reply.message()
	
	author = ctx.get_guild().get_member(ctx.author)

	if Utilities.IsAdmin(author):
		await leave_interface.InsertRetroactiveLeave(ctx.options.discorduser, msg.id, datetime.datetime.strptime(ctx.options.startdate, "%Y-%m-%d"), datetime.datetime.strptime(ctx.options.enddate, "%Y-%m-%d"), ctx.options.leavetype, ctx.options.isemergency, ctx.options.isunpaid, ctx.options.reason)
		embed = UI.CreateLeavesBalancesEmbed(ctx.options.discorduser, ctx.author.id)
		await ctx.author.send(embed = embed)

	else:
		await ctx.author.send(content = "This command is for Admins only")

	await msg.delete()

@bot.command
@lightbulb.command(name = "showleavesbalance", description = "Shows your leaves balance", guilds = guild_ids)
@lightbulb.implements(lightbulb.SlashCommand)
async def ShowLeavesBalance(ctx):
	embed = UI.CreateLeavesBalancesEmbed(ctx.author)
	if embed != None:
		await ctx.author.send(embed = embed)

	else:
		await ctx.author.send(content = "Your request failed, try again later.")

	await ctx.respond(content = "Done", delete_after = deletion_timer)

@bot.command
@lightbulb.command(name = "ismemberworking", description = "Checks if a member is working on a given day", guilds = guild_ids)
@lightbulb.implements(lightbulb.SlashCommand)
async def IsMemberWorking(ctx):
	is_working, reason = leave_interface.IsMemberWorking(ctx.options.discorduser.id, datetime.datetime.strptime(ctx.options.date, "%Y-%m-%d"))
	
	author = ctx.get_guild().get_member(ctx.author)

	if Utilities.IsAdmin(author):
		await ctx.author.send(content = f"{is_working}, {reason}")

	else:
		await ctx.author.send(content = f"{is_working}")

	await ctx.respond(content = "Done", delete_after = deletion_timer)

@bot.command
@lightbulb.command(name = "getendofmonthreport", description = "Returns a report of the selected users for the provided month", guilds = guild_ids)
@lightbulb.implements(lightbulb.SlashCommand)
async def GetEndOfMonthReport(ctx):
	author = ctx.get_guild().get_member(ctx.author)

	if Utilities.IsAdmin(author):
		members_list = Utilities.GetMembersFromMention(ctx.options.members) or member_db.GetMembers()
		embed = UI.CreateGetEndOfMonthReportEmbed(members_list, ctx.options.month, ctx.options.year)
		await ctx.author.send(embed = embed)

	else:
		await ctx.author.send(content = "This command is for Admins only")

	await ctx.respond(content = "Done", delete_after = deletion_timer)

@bot.command
@lightbulb.command(name = "getendofyearreport", description = "Returns a report of the selected users for the provided year", guilds = guild_ids)
@lightbulb.implements(lightbulb.SlashCommand)
async def GetEndOfYearReport(ctx):
	author = ctx.get_guild().get_member(ctx.author)

	if Utilities.IsAdmin(author):
		members_list = Utilities.GetMembersFromMention(ctx.options.members) or member_db.GetMembers()
		embed = UI.CreateGetEndOfYearReportEmbed(members_list, year)
		await ctx.author.send(embed = embed)

	else:
		await ctx.author.send(content = "This command is for Admins only")

	await ctx.respond(content = "Done", delete_after = deletion_timer)

@bot.command
@lightbulb.command(name="iseveryonehere", description = "Checks if all working 'Full Time' members are in the meeting channel", guilds = guild_ids)
@lightbulb.implements(lightbulb.SlashCommand)
async def IsEveryoneHere(ctx):
	today = datetime.datetime.today().date()
	today = datetime.datetime(today.year, today.month, today.day)

	guild = ctx.get_guild()
	meeting_channel = guild.get_channel(int(os.getenv("MeetingChannel_id")))
	author = ctx.get_guild().get_member(ctx.author)

	roles = await guild.fetch_roles()
	fulltime_role = lightbulb.utils.get(roles, id = int(os.getenv("Full_Time_Role_id")))
	non_core_roles = os.getenv("Non_Core_Attending_Role_ids").split(", ")
	non_core_roles = set([lightbulb.utils.get(roles, id = int(role_id)) for role_id in non_core_roles])

	core_attending_members = list(filter(lambda member: (fulltime_role in roles) and not non_core_roles.intersection(set(roles)), guild.get_members()))
	core_attending_members_in_voicechannel = list(filter(lambda member : fulltime_role in roles, bot.cache.get_voice_states_view_for_channel(guild.id, meeting_channel)))
	not_here = list(set(core_attending_members) - set(core_attending_members_in_voicechannel))

	approved_leaves = list(filter(lambda member : (leave_interface.IsMemberOnLeave(member.id, today))[0], not_here))
	approved_leaves_names = [member.display_name for member in approved_leaves]
	approved_leaves_reasons = [leave_interface.IsMemberOnLeave(member.id, today)[1] for member in approved_leaves]
	approved_leaves_dict = dict(zip(approved_leaves_names, approved_leaves_reasons))

	missing_members = list(set(not_here) - set(approved_leaves))
	missing_members = [member.display_name for member in missing_members]
	
	embed = UI.CreateIsEveryoneHereEmbed(approved_leaves_dict, missing_members, Utilities.IsAdmin(author))

	await ctx.author.send(embed = embed)
	await ctx.respond(content="Done", delete_after = deletion_timer)

@bot.command
@lightbulb.command(name = "creditleaves", description = "Inserts an extra credit for the provided leave type", guilds = guild_ids)
@lightbulb.implements(lightbulb.SlashCommand)
async def CreditLeaves(ctx):
	author = ctx.get_guild().get_member(ctx.author)

	if Utilities.IsAdmin(author):
		print(ctx.options.dayscount)
		leave_db.InsertExtraBalance(datetime.datetime.today(), ctx.author.id, ctx.options.discorduser.id, ctx.options.leavetype, ctx.options.reason, ctx.options.dayscount)
		embed = UI.CreateLeavesBalancesEmbed(ctx.options.discorduser, ctx.author.id)
		await ctx.author.send(embed = embed)

	else:
		await ctx.author.send(content = "This command is for Admins only")

	await ctx.respond(content = "Done", delete_after = deletion_timer)

@bot.command
@lightbulb.command(name = "getleavesbetween", description = "Returns the leaves of one/all members in the provided dates range", guilds = guild_ids)
@lightbulb.implements(lightbulb.SlashCommand)
async def GetLeavesBetween(ctx):
	leaves = leave_interface.GetLeavesAcrossRange(startdate, enddate, discorduser)
	embed = UI.CreateLeavesAcrossRangeEmbed(leaves, startdate, enddate, Utilities.IsAdmin(ctx.author))
	await ctx.author.send(embed = embed)
	await ctx.respond(content = "Done", delete_after = deletion_timer)

def InsertOptionsToCommand(options, function_name):
	for option in options:
		function_name.options[option] = options[option]

InsertOptionsToCommand(UI.CreateLeaveRequestOptions(), RequestLeave)
InsertOptionsToCommand(UI.CreateMemberInsertionOptions(), InsertMember)
InsertOptionsToCommand(UI.CreateRetroactiveLeaveInsertionOptions(), InsertRetroactiveLeave)
InsertOptionsToCommand(UI.CreateIsMemberWorkingOptions(), IsMemberWorking)
InsertOptionsToCommand(UI.CreateGetEndOfMonthReportOptions(), GetEndOfMonthReport)
InsertOptionsToCommand(UI.CreateGetEndOfYearReportOptions(), GetEndOfYearReport)
InsertOptionsToCommand(UI.CreateCreditLeavesOptions(), CreditLeaves)
InsertOptionsToCommand(UI.CreateGetLeavesAcrossRangeOptions(), GetLeavesBetween)

bot.run()