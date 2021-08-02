import discord
import os

from datetime import date, timedelta, datetime
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from discord_components import DiscordComponents, Button, Select, SelectOption
from discord_components.component import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice

client= commands.Bot(command_prefix="!", intents=discord.Intents.default())
slash= SlashCommand(client, sync_commands=True)
load_dotenv()

guild_ids= [int(os.getenv("TestServer_id"))]

approve_btn= Button(label='Approve', style = ButtonStyle.green, custom_id='approve_btn')
reject_btn= Button(label='Reject', style = ButtonStyle.red, custom_id='reject_btn')

max_allowed_days = 3

@client.event
async def on_ready():
    DiscordComponents(client)
    print("the bot is ready")


async def CreateAnnualLeaveEmbed(ctx, startdate, enddate):
    embed = discord.Embed(
        title="Annual Leave Request", 
        description=f'{ctx.author.mention} is requesting a leave', 
        colour=0x4682B4
    )
    embed.set_thumbnail(url= os.getenv("Annual_Leave_Link"))
    embed.add_field(name= "Start Date", value= startdate, inline= True)
    embed.add_field(name= "End Date", value= enddate, inline= True)
    embed.set_footer(text = date.today())

    return embed


async def ApproveLeave(author):
    await author.send(content = "Your annual leave request was approved")

async def RejectLeave(author):
    await author.send(content = "Your annual leave request was rejected")

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

def CreateDateOptions():
    requestLeave_options = [
        create_option(
            name= "startdate",
            description= "starting date of your leave",
            option_type= 3,
            required= True,
            choices= CreateDateChoices()
        ),
        create_option(
            name= "enddate",
            description= "Leave empty for 1 day leave",
            option_type= 3,
            required= True,
            choices= CreateDateChoices()
        )
    ]

    return requestLeave_options

def CreateDateChoices():
    firstDate = date.today() + timedelta(1)
    current_time = datetime.now().hour
    dateChoices = []
    if current_time > 13:
        firstDate = date.today() + timedelta(2)
    
    for i in range(25):
        tmpDate = firstDate + timedelta(i)
        weekDay = tmpDate.strftime("%A")
        dateChoices.append(create_choice(name = weekDay +": "+ tmpDate.strftime('%m/%d/%Y'), value = tmpDate.strftime('%m/%d/%Y')))
    
    return dateChoices

def CheckAvailableLeaves(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    requestedDays = (eDate - sDate).days

    if max_allowed_days >= requestedDays :
        return int(os.getenv("Abdo_days")) - requestedDays
    else:
        return -1

def ValidateDates(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    return eDate > sDate


@slash.slash(name= "RequestLeave", description= "Request an annual leave", options= CreateDateOptions(), guild_ids= guild_ids)
async def RequestLeave(ctx, startdate, enddate):
    teamLead= await client.fetch_user(int(os.getenv("Abdo_id")))
    message= None

    if teamLead!= None:
        if ValidateDates(startdate, enddate):
            if CheckAvailableLeaves(startdate, enddate) >= 0 :
                await ctx.send(content = f"Your Annual leave request has been sent")
                embed= await CreateAnnualLeaveEmbed(ctx, startdate, enddate)
                message= await teamLead.send(embed=embed, components = [[approve_btn, reject_btn]])
                await HandleButtonClick(ctx, teamLead, message)
            else:
                await ctx.send(content = "You dont have enough leaves to request you current balance is " + str(int(os.getenv("Abdo_days"))))
        else:
            await ctx.send(content = "Please select valid dates")
        

    else:
        await ctx.send(content = "Your Request has failed, try again later")



client.run(os.getenv("Bot_token"))
