import discord
import os
import UI
import db
import member_module as mm
import leave_module as lm

from dotenv import load_dotenv
from datetime import datetime
from discord.ext import commands
from discord_slash import SlashCommand
from discord_components import DiscordComponents

load_dotenv()
db.load_db()

client = commands.Bot(command_prefix = "!", intents = discord.Intents.default())
slash = SlashCommand(client, sync_commands = True)

guild_ids = [int(os.getenv("TestServer_id"))]

@client.event
async def on_ready():
    DiscordComponents(client)
    print("the bot is ready")

@client.event
async def on_raw_reaction_add(payload):
    await UI.HandleLeaveReactions(client, payload)

@slash.slash(name = "RequestLeave", description = "Request an annual leave", options = UI.CreateDateOptions(), guild_ids = guild_ids)
async def RequestLeave(ctx, leavetype, startdate, enddate, reason = ""):
    leavesChannel = await client.fetch_channel(int(os.getenv("TestChannel_id")))
    await lm.RequestLeave(ctx, client, leavetype, startdate, enddate, leavesChannel, reason)

@slash.slash(name = "InsertMember", description = "Insert new member into the database", options = UI.CreateMemberOptions(), guild_ids = guild_ids)
async def InsertMember(ctx, discorduser, name, email, startdate, leavedate, position):
    result = mm.InsertMember(discorduser.id, name, email, datetime.strptime(startdate, '%m/%d/%Y'), datetime.strptime(leavedate, '%m/%d/%Y'), position)
    await ctx.send(content = "Success" if result else "Failed")

@slash.slash(name = "CheckBalance", description = "Checks the available leave balance", options = UI.CreateBalanceOptions(), guild_ids = guild_ids)
async def CheckBalance(ctx, leavetype):
    result = lm.GetLeaveBalance(ctx.author.id, leavetype)
    await ctx.author.send(content = str(result))
    await ctx.send(content = "Request was sent")

@slash.slash(name = "CheckBalanceForMemeber", description = "Checks the available leave balance for a certain member", options = UI.CreateBalanceForMemeberOptions(), guild_ids = guild_ids)
@commands.has_role("Admin")
async def CheckBalanceForMemeber(ctx, discorduser, leavetype):
    try:
        result = lm.GetLeaveBalance(discorduser.id, leavetype)
        await ctx.author.send(content = str(result))
        await ctx.send(content = "Request was sent")
    except Exception as e:
        print(e)
        await ctx.send(content = "This command can only be used by an Admin")
   

client.run(os.getenv("Bot_token"))
