import discord
import os

from Leaves import *
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from discord_components import DiscordComponents, Button, Select, SelectOption, message

load_dotenv()

client= commands.Bot(command_prefix="!", intents=discord.Intents.default())
slash= SlashCommand(client, sync_commands=True)

guild_ids= [int(os.getenv("TestServer_id"))]

@client.event
async def on_ready():
    DiscordComponents(client)
    print("the bot is ready")

async def HandleButtonClick(ctx, user, message):
    if message != None:
        def check(res):
            return res.message.id == message.id

        status = await client.wait_for("button_click", check = check)
        clickedButton = status.component.custom_id

        if clickedButton == "approve_btn":
            await status.respond(content = "The request has been approved")
            await ApproveLeave(ctx.author)

        elif clickedButton == "reject_btn":
            await status.respond(content = "The request has been rejected")
            await RejectLeave(ctx.author)

    else:
        await user.send("Your Request has failed, try again later")


@slash.slash(name= "RequestLeave", description= "Request an annual leave", options= CreateDateOptions(), guild_ids= guild_ids)
async def RequestLeave(ctx, startdate, enddate):
    teamLead= await client.fetch_user(int(os.getenv("Abdo_id")))
    message = await RequestAnnualLeave(ctx, startdate, enddate, teamLead)

    if message != "":
        await HandleButtonClick(ctx, teamLead, message)


client.run(os.getenv("Bot_token"))
