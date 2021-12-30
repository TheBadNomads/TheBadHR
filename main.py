from datetime import datetime
import discord
import os
import Utilities
import Scheduler

from discord import utils
import UI
import db

from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from discord_components import DiscordComponents, Button, Select, SelectOption, message
from Member import member_db 
from Leave import leave_interface, leave_db

load_dotenv()

client = commands.Bot(command_prefix = "!", intents = discord.Intents.all())
slash = SlashCommand(client, sync_commands = True)

guild_ids = [int(os.getenv("TestServer_id"))]

@client.event
async def on_ready():
    DiscordComponents(client)
    print("the bot is ready")

@client.event
async def on_raw_reaction_add(payload):
    await leave_interface.HandleLeaveReactions(client, payload)

@slash.slash(name = "RequestLeave", description = "Requests an annual leave", options = UI.CreateLeaveRequestOptions(), guild_ids = guild_ids)
async def RequestLeave(ctx, leavetype, startdate, enddate, reason = ""):
    message_content = await leave_interface.ProcessLeaveRequest(ctx, ctx.author, client, leavetype, datetime.strptime(startdate, '%d/%m/%Y'), datetime.strptime(enddate, '%d/%m/%Y'), reason)
    await ctx.author.send(content = message_content)
    await ctx.send(content = "Done", delete_after = 0.1)

@slash.slash(name = "InsertMember", description = "Inserts a new member into the database", options = UI.CreateMemberInsertionOptions(), guild_ids = guild_ids)
async def InsertMember(ctx, discorduser, name, email, startdate):
    message_content = ""
    if Utilities.IsAdmin(ctx.author):
        message_content = member_db.InsertMember(discorduser.id, name, email, datetime.strptime(startdate, '%d/%m/%Y'))
    else:
        message_content = "This command is for Admins only"

    await ctx.author.send(content = message_content)
    await ctx.send(content = "Done", delete_after = 0.1)

@slash.slash(name = "InsertRetroactiveLeave", description = "Inserts a late leave (Admins Only)", options = UI.CreateRetroactiveLeaveInsertionOptions(), guild_ids = guild_ids)
async def InsertRetroactiveLeave(ctx, discorduser, leavetype, startdate, enddate, isemergency, isunpaid, reason = ""):
    message_content = ""
    await ctx.send(content = "Processing")
    if Utilities.IsAdmin(ctx.author):
        message_content = await leave_interface.InsertRetroactiveLeave(discorduser, ctx.message.id, datetime.strptime(startdate, '%d/%m/%Y'), datetime.strptime(enddate, '%d/%m/%Y'), leavetype, isemergency, isunpaid, reason)
    else:
        message_content = "This command is for Admins only"
        
    await ctx.author.send(content = message_content)
    await ctx.message.delete()

@slash.slash(name = "ShowLeavesBalance", description = "Shows your leaves balance", guild_ids = guild_ids)
async def ShowLeavesBalance(ctx):
    embed = UI.CreateLeavesBalancesEmbed(ctx.author.id)
    if embed != None:
        await ctx.author.send(embed = embed)
    else:
        await ctx.author.send(content = "your request failed, try again later")

    await ctx.send(content = "Done", delete_after = 0.1)

@slash.slash(name = "IsMemberWorking", description = "Checks if a member is working on a given day", options = UI.CreateIsMemberWorkingOptions(), guild_ids = guild_ids)
async def IsMemberWorking(ctx, discorduser, date = datetime.today().strftime('%d/%m/%Y')):
    is_working, reason = leave_interface.IsMemberWorking(discorduser.id, datetime.strptime(date, '%d/%m/%Y'))
    if Utilities.IsAdmin(ctx.author):
        await ctx.author.send(content = f"{is_working}, {reason}")
    else:
        await ctx.author.send(content = f"{is_working}")

    await ctx.send(content = "Done", delete_after = 0.1)

@slash.slash(name = "GetEndOfMonthReport", description = "Returns a report of the selected users for the provided month", options = UI.CreateGetEndOfMonthReportOptions(), guild_ids = guild_ids)
async def GetEndOfMonthReport(ctx, month = None, year = None):
    if Utilities.IsAdmin(ctx.author):
        embed = UI.CreateGetEndOfMonthReportEmbed(member_db.GetMembers(), month, year)
        await ctx.author.send(embed = embed)
    else:
        await ctx.author.send(content = "This command is for Admins only")

    await ctx.send(content = "Done", delete_after = 0.1)

@slash.slash(name="IsEveryoneHere", description = "Checks if all working 'Full Time' members are in the meeting channel", guild_ids = guild_ids)
async def IsEveryoneHere(ctx):

    today = datetime.today().date()
    today = datetime(today.year, today.month, today.day)

    guild = client.guilds[0]
    meeting_channel = client.get_channel(int(os.getenv("MeetingChannel_id")))
    fulltime_role = discord.utils.get(guild.roles, name = "Full Time")
    
    fulltime_members = list(filter(lambda member: fulltime_role in member.roles, guild.members))
    fulltime_members_in_voicechannel = list(filter(lambda member : fulltime_role in member.roles, meeting_channel.members))
    not_here = list(set(fulltime_members) - set(fulltime_members_in_voicechannel))

    approved_leaves = list(filter(lambda member : (leave_interface.IsMemberOnLeave(member.id, today))[0], not_here))
    approved_leaves_names = [member.display_name for member in approved_leaves]
    approved_leaves_reasons = [leave_interface.IsMemberOnLeave(member.id, today)[1] for member in approved_leaves]
    approved_leaves_dict = dict(zip(approved_leaves_names, approved_leaves_reasons))

    missing_members = list(set(not_here) - set(approved_leaves))
    missing_members = [member.display_name for member in missing_members]
    
    embed = UI.CreateIsEveryoneHereEmbed(approved_leaves_dict, missing_members, Utilities.IsAdmin(ctx.author))

    await ctx.author.send(embed = embed)
    await ctx.send(content="Done", delete_after=0.1)

@slash.slash(name = "CreditLeaves", description = "Inserts an extra credit for the provided leave type", options = UI.CreateCreditLeavesOptions(), guild_ids = guild_ids)
async def CreditLeaves(ctx, discorduser, leavetype, dayscount = 1, reason = ""):
    if Utilities.IsAdmin(ctx.author):
        leave_db.InsertExtraBalance(datetime.today(), ctx.author.id, discorduser.id, leavetype, reason, dayscount)
        embed = UI.CreateLeavesBalancesEmbed(discorduser, ctx.author.id)
        await ctx.author.send(embed = embed)
    else:
        await ctx.author.send(content = "This command is for Admins only")

    await ctx.send(content = "Done", delete_after = 0.1)

@slash.slash(name = "GetLeavesBetween", description = "Returns the leaves of one/all members in the provided dates range", options = UI.CreateGetLeavesAcrossRangeOptions(), guild_ids = guild_ids)
async def GetLeavesBetween(ctx, startdate, enddate, discorduser = None):
    leaves = leave_interface.GetLeavesAcrossRange(startdate, enddate, discorduser)
    embed = UI.CreateLeavesAcrossRangeEmbed(leaves, startdate, enddate, Utilities.IsAdmin(ctx.author))
    await ctx.author.send(embed = embed)
    await ctx.send(content = "Done", delete_after = 0.1)

client.run(os.getenv("Bot_token"))
