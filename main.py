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

@slash.slash(name = "RequestLeave", description = "Requests an annual leave", options = UI.CreateDateOptions(), guild_ids = guild_ids)
async def RequestLeave(ctx, leavetype, startdate, enddate, reason = ""):
    message_content = await leave_interface.ProcessLeaveRequest(ctx, ctx.author, client, leavetype, datetime.strptime(startdate, '%d/%m/%Y'), datetime.strptime(enddate, '%d/%m/%Y'), reason)
    await ctx.author.send(content = message_content)
    await ctx.send(content = "Done", delete_after = 0.1)

@slash.slash(name = "InsertMember", description = "Inserts new member into the database", options = UI.CreateMemberOptions(), guild_ids = guild_ids)
async def InsertMember(ctx, discorduser, name, email, startdate):
    message_content = ""
    if Utilities.IsAdmin(ctx.author):
        message_content = member_db.InsertMember(discorduser.id, name, email, datetime.strptime(startdate, '%d/%m/%Y'))
    else:
        message_content = "This command is for Admins only"

    await ctx.author.send(content = message_content)
    await ctx.send(content = "Done", delete_after = 0.1)
   
@slash.slash(name = "ShowLeavesBalance", description = "Returns your leaves balances", guild_ids = guild_ids)
async def ShowLeavesBalance(ctx):
    embed = UI.CreateLeavesBalancesEmbed(ctx)
    if embed == None:
        await ctx.send(content = "your request failed, try again later")
    else:
        await ctx.send(content = "your request succeeded")
        await ctx.author.send(embed = embed)

client.run(os.getenv("Bot_token"))
