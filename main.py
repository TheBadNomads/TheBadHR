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

@slash.slash(name = "RequestLeave", description = "Request an annual leave", options = UI.CreateLeaveRequestOptions(), guild_ids = guild_ids)
async def RequestLeave(ctx, leavetype, startdate, enddate, reason = ""):
    await leave_interface.ProcessLeaveRequest(ctx, ctx.author, client, leavetype, datetime.strptime(startdate, '%d/%m/%Y'), datetime.strptime(enddate, '%d/%m/%Y'), reason)

@slash.slash(name = "InsertMember", description = "Insert a new member into the database", options = UI.CreateMemberInsertionOptions(), guild_ids = guild_ids)
async def InsertMember(ctx, discorduser, name, email, startdate):
    if Utilities.IsAdmin(ctx.author):
        result = member_db.InsertMember(discorduser.id, name, email, datetime.strptime(startdate, '%d/%m/%Y'))
        await ctx.send(content = result)
    else:
        await ctx.send(content = "This command is for Admins only")

@slash.slash(name = "InsertLateLeave", description = "Insert a late leave (Admins Only)", options = UI.CreateLateLeaveInsertionOptions(), guild_ids = guild_ids)
async def InsertLateLeave(ctx, discorduser, leavetype, startdate, enddate, reason = ""):
    if Utilities.IsAdmin(ctx.author):
        await leave_interface.InsertLateLeave(ctx, discorduser, datetime.strptime(startdate, '%d/%m/%Y'), datetime.strptime(enddate, '%d/%m/%Y'), leavetype, reason)
    else:
        await ctx.send(content = "This command is for Admins only")

client.run(os.getenv("Bot_token"))
