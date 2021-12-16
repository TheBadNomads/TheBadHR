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

    await ctx.send(content = "Done", delete_after = 0.1)

@slash.slash(name = "IsMemberWorking", description = "Checks if a member is working on a given day", options = UI.CreateIsMemberWorkingOptions(), guild_ids = guild_ids)
async def IsMemberWorking(ctx, discorduser, date = datetime.today().strftime('%d/%m/%Y')):
    is_working, reason = leave_interface.IsMemberWorking(discorduser.id, datetime.strptime(date, '%d/%m/%Y'))
    if Utilities.IsAdmin(ctx.author):
        await ctx.author.send(content = f"{is_working}, {reason}")
    else:
        await ctx.author.send(content = f"{is_working}")

    await ctx.send(content = "Done", delete_after = 0.1)

@slash.slash(name="IsEveryoneHere", description="Checks if all working 'Full Time' members are in voice channel", guild_ids=guild_ids)
async def IsEveryoneHere(ctx, date = datetime.today().strftime('%d/%m/%Y')):

    guild = client.guilds[0]
    fulltime_role = discord.utils.get(guild.roles, name = "Full Time")

    # Check if author is in a voice channel
    if ctx.author.voice and ctx.author.voice.channel:

        # Get all users with 'Full Time' role
        fulltime_member_list = list(filter(lambda user: fulltime_role in user.roles, guild.members))
        
        # Get all users with 'Full Time' role who are in the channel
        vc_fulltime_member_list = list(filter(lambda user : fulltime_role in user.roles, ctx.author.voice.channel.members))

        # Get all users with 'Full Time' role who are not in voice channel
        not_here = list(set(fulltime_member_list) - set(vc_fulltime_member_list))

        # Check if user is working today and removes them if they have leave
        not_here = list(filter(lambda user : (leave_interface.IsMemberWorking(user.id, datetime.strptime(date, '%d/%m/%Y')))[0], not_here))

        # Use display name
        not_here = [user.display_name for user in not_here]
        
        if not not_here:
            await ctx.author.send(content="Everyone's Here!")
        else:
            await ctx.author.send(content="Users not here: " + (', '.join(not_here)))
        
    else:
        await ctx.author.send(content="You need to be in a voice channel to use this command")

    await ctx.send(content="Done", delete_after=0.1)

client.run(os.getenv("Bot_token"))