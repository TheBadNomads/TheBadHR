import discord
import os

from discord import team
from db import *
from Leaves import *
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from discord_components import DiscordComponents, Button, Select, SelectOption, message

load_dotenv()
load_db()

client= commands.Bot(command_prefix="!", intents=discord.Intents.default())
slash= SlashCommand(client, sync_commands=True)

guild_ids= [int(os.getenv("TestServer_id"))]

@client.event
async def on_ready():
    DiscordComponents(client)
    print("the bot is ready")

@slash.slash(name= "RequestLeave", description= "Request an annual leave", options= CreateDateOptions(), guild_ids= guild_ids)
async def RequestLeave(ctx, leavetype, startdate, enddate):
    await ctx.send(content= GetUserByID(2))
    # teamLead= await client.fetch_user(int(os.getenv("Abdo_id")))
    # current_time= datetime.now().hour

    # if leavetype == "annual":
    #     if current_time > 12:
    #         await SendWarningMessage(ctx= ctx, client= client, startdate= startdate, enddate= enddate, teamLead= teamLead)
    #     else:
    #         await RequestAnnualLeave(ctx= ctx, client= client, startdate= startdate, enddate= enddate, teamLead= teamLead)
            
    # elif leavetype == "emergency":
    #     await RequestEmergencyLeave(ctx= ctx, client= client, startdate= startdate, enddate= enddate, teamLead= teamLead)

    # elif leavetype == "sick":
    #     await RequestSickLeave(ctx= ctx, client= client, startdate= startdate, enddate= enddate, teamLead= teamLead)

client.run(os.getenv("Bot_token"))
