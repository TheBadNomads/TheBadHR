import discord
import os
import Leaves
import UI
import db

from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from discord_components import DiscordComponents, Button, Select, SelectOption, message

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
async def RequestLeave(ctx, leavetype, startdate, enddate):
    leavesChannel = await client.fetch_channel(int(os.getenv("TestChannel_id")))
    await Leaves.RequestLeave(ctx, client, leavetype, startdate, enddate, leavesChannel)
   

client.run(os.getenv("Bot_token"))
