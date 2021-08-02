import discord
import os

from datetime import date, timedelta, datetime
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from discord_components import DiscordComponents, Button, Select, SelectOption
from discord_components.component import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice

load_dotenv()

approve_btn= Button(label= 'Approve', style= ButtonStyle.green, custom_id= 'approve_btn')
reject_btn= Button(label= 'Reject', style= ButtonStyle.red, custom_id= 'reject_btn')

continue_btn= Button(label= 'Continue', style= ButtonStyle.gray, custom_id= 'continue_btn')
cancel_btn= Button(label= 'Cancel', style= ButtonStyle.red, custom_id= 'cancel_btn')

def CreateAnnualLeaveEmbed(ctx, startdate, enddate):
    embed = discord.Embed(
        title= "Annual Leave Request", 
        description= f'{ctx.author.mention} is requesting a leave', 
        colour= 0x4682B4
    )
    embed.set_thumbnail(url= os.getenv("Annual_Leave_Link"))
    embed.add_field(name= "Start Date", value= startdate, inline= True)
    embed.add_field(name= "End Date", value= enddate, inline= True)
    embed.set_footer(text = date.today())

    return embed

def CreateWarningEmbed():
    embed = discord.Embed(
        title= "Annual Leave Request", 
        description= "It is past core hours you leave request with be considered as an emergency leave", 
        colour= 0xFF0000
    )

    return embed

async def RequestAnnualLeave(ctx, startdate, enddate, teamLead):
    current_time= datetime.now().hour

    if current_time < 13:
        await WaitForUserConfirmation(ctx, startdate, enddate, teamLead)
    else:
        return await CompleteLeaveRequest(ctx, startdate, enddate, teamLead)


async def WaitForUserConfirmation(ctx, startdate, enddate, teamLead):
    await ctx.send(content= GetCaption(7))
    await ctx.author.send(embed=CreateWarningEmbed(), components = [[continue_btn, cancel_btn]])

    return ""


async def CompleteLeaveRequest(ctx, startdate, enddate, teamLead):
    message= None
    if teamLead!= None:
        if ValidateDates(startdate, enddate):
            if CheckAvailableLeaves(startdate, enddate) >= 0 :
                await ctx.send(content= GetCaption(1))
                embed= CreateAnnualLeaveEmbed(ctx, startdate, enddate)
                message= await teamLead.send(embed=embed, components = [[approve_btn, reject_btn]])

                return message

            else:
                await ctx.send(content= GetCaption(2))

        else:
            await ctx.send(content= GetCaption(3))
        
    else:
        await ctx.send(content= GetCaption(4))

    return ""

def CheckAvailableLeaves(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    requestedDays = (eDate - sDate).days

    return int(os.getenv("Abdo_days")) - requestedDays

def ValidateDates(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    return eDate >= sDate

async def ApproveLeave(author):
    await author.send(content= GetCaption(5))

async def RejectLeave(author):
    await author.send(content= GetCaption(6))


def CreateDateChoices():
    firstDate = date.today() + timedelta(1)
    dateChoices = []
    
    for i in range(25):
        tmpDate = firstDate + timedelta(i)
        weekDay = tmpDate.strftime("%A")
        dateChoices.append(create_choice(name = weekDay +": "+ tmpDate.strftime('%m/%d/%Y'), value = tmpDate.strftime('%m/%d/%Y')))
    
    return dateChoices

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

def GetCaption(captionCode):
    switcher = {
        1: "Your Annual leave request has been sent",
        2: "You dont have enough leaves to request you current balance is " + str(int(os.getenv("Abdo_days"))),
        3: "Please select valid dates",
        4: "Your Request has failed, try again later",
        5: "Your annual leave request was approved",
        6: "Your annual leave request was rejected",
        7: "Your request is being processed"
    }

    return switcher.get(captionCode, lambda: "Invalid caption code")