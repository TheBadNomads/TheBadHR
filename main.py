from datetime import datetime
import discord
import os
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

@slash.slash(name = "RequestLeave", description = "Request an annual leave", options = UI.CreateDateOptions(), guild_ids = guild_ids)
async def RequestLeave(ctx, leavetype, startdate, enddate, reason = ""):
    await leave_interface.RequestLeave(ctx, ctx.author, client, leavetype, datetime.strptime(startdate, '%d/%m/%Y'), datetime.strptime(enddate, '%d/%m/%Y'), reason)

@slash.slash(name = "InsertMember", description = "Insert new member into the database", options = UI.CreateMemberOptions(), guild_ids = guild_ids)
async def InsertMember(ctx, discorduser, name, email, startdate):
    result = member_db.InsertMember(discorduser.id, name, email, datetime.strptime(startdate, '%d/%m/%Y'))
    await ctx.send(content = result)
   

client.run(os.getenv("Bot_token"))
