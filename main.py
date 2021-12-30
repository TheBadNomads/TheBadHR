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
    Scheduler.Setup(client)
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

@slash.slash(name = "CreditLeaves", description = "Inserts an extra credit for the provided leave type", options = UI.CreateCreditLeavesOptions(), guild_ids = guild_ids)
async def CreditLeaves(ctx, discorduser, leavetype, dayscount = 1, reason = ""):
    message_content = ""
    if Utilities.IsAdmin(ctx.author):
        message_content = leave_db.InsertExtraBalance(datetime.today(), ctx.author.id, discorduser.id, leavetype, reason, dayscount)
    else:
        message_content = "This command is for Admins only"

    await ctx.author.send(content = message_content)
    await ctx.send(content = "Done", delete_after = 0.1)

@slash.slash(name = "GetLeavesBetween", description = "Returns the leaves of one/all members in the provided dates range", options = UI.CreateGetLeavesAcrossRangeOptions(), guild_ids = guild_ids)
async def GetLeavesBetween(ctx, startdate, enddate, discorduser = None):
    leaves = leave_interface.GetLeavesAcrossRange(startdate, enddate, discorduser)
    embed = UI.CreateLeavesAcrossRangeEmbed(leaves, startdate, enddate, Utilities.IsAdmin(ctx.author))
    await ctx.author.send(embed = embed)
    await ctx.send(content = "Done", delete_after = 0.1)

client.run(os.getenv("Bot_token"))
