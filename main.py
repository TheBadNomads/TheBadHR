from datetime import datetime
import discord
import os
import Utilities

from discord import utils
import UI
import db

from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from discord_components import DiscordComponents, Button, Select, SelectOption, message
from Member import member_db 
from Leave import leave_interface

load_dotenv()

client = commands.Bot(command_prefix = "!", intents = discord.Intents.default())
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

@slash.slash(name = "IsMemberOnLeave", description = "Checks if the required member is on leave for the requested day", options = UI.CreateIsMemberOnLeaveOptions(), guild_ids = guild_ids)
async def IsMemberOnLeave(ctx, discorduser, date):
    is_on_leave, reason = leave_interface.IsMemberOnLeave(discorduser.id, date)
    if Utilities.IsAdmin(ctx.author):
        await ctx.author.send(content = str(is_on_leave) + ", " + reason)
    else:
        await ctx.author.send(content = is_on_leave)
        
    await ctx.send(content = "Done", delete_after = 0.1)

client.run(os.getenv("Bot_token"))
