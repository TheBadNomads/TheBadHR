import discord
import os
import Leaves

from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from discord_components import DiscordComponents, Button, Select, SelectOption, message

load_dotenv()

client = commands.Bot(command_prefix ="!", intents =discord.Intents.default())
slash = SlashCommand(client, sync_commands =True)

guild_ids = [int(os.getenv("TestServer_id"))]

@client.event
async def on_ready():
    DiscordComponents(client)
    print("the bot is ready")

@slash.slash(name = "RequestLeave", description = "Request an annual leave", options = UI.CreateDateOptions(), guild_ids = guild_ids)
async def RequestLeave(ctx, leavetype, startdate, enddate):
    Leaves.RequestLeave(ctx, client, leavetype, startdate, enddate)
   

client.run(os.getenv("Bot_token"))
