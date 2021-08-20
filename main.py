import discord
import os
import UI
import db

from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from discord_components import DiscordComponents, Button, Select, SelectOption, message
from Member import member_interface as mi
from Leave import leave_interface as li

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
    await li.HandleLeaveReactions(client, payload)

@slash.slash(name = "RequestLeave", description = "Request an annual leave", options = UI.CreateDateOptions(), guild_ids = guild_ids)
async def RequestLeave(ctx, leavetype, startdate, enddate, reason = ""):
    await li.RequestLeave(ctx, client, leavetype, startdate, enddate, reason)

@slash.slash(name = "CheckBalance", description = "Checks the available leave balance", options = UI.CreateBalanceOptions(), guild_ids = guild_ids)
async def CheckBalance(ctx, leavetype):
    result = li.GetLeaveBalance(ctx.author.id, leavetype)
    await ctx.author.send(content = str(result))
    await ctx.send(content = "Request was sent")

@slash.slash(name = "InsertMember", description = "Insert new member into the database", options = UI.CreateMemberOptions(), guild_ids = guild_ids)
async def InsertMember(ctx, discorduser, name, email, startdate, leavedate, position):
    result = mi.InsertMember(discorduser.id, name, email, startdate, leavedate, position)
    await ctx.send(content = "Success" if result else "Failed")
   

client.run(os.getenv("Bot_token"))
