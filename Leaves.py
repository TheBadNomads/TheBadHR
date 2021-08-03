import discord
import os

from datetime import date, timedelta, datetime
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from discord_components import DiscordComponents, Button, Select, SelectOption
from discord_components.component import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice

# global vars
approve_btn= Button(label= 'Approve', style= ButtonStyle.green, custom_id= 'approve_btn')
reject_btn= Button(label= 'Reject', style= ButtonStyle.red, custom_id= 'reject_btn')

continue_btn= Button(label= 'Continue', style= ButtonStyle.gray, custom_id= 'continue_btn')
cancel_btn= Button(label= 'Cancel', style= ButtonStyle.red, custom_id= 'cancel_btn')

async def RequestAnnualLeave(ctx, client, startdate, enddate, teamLead):
    current_time= datetime.now().hour

    if current_time > 12:
        return await RequestEmergencyLeave(ctx, client, startdate, enddate, teamLead)
    else:
        return await CompleteLeaveRequest(ctx, client, startdate, enddate, teamLead)

async def RequestEmergencyLeave(ctx, client, startdate, enddate, teamLead):
    message= ""
    await ctx.send(content= GetCaption(7))
    message= await ctx.author.send(embed=CreateWarningEmbed(), components = [[continue_btn, cancel_btn]])
    await HandleWarningButtons(ctx= ctx, client= client, message= message, startdate= startdate, enddate= enddate, teamLead= teamLead)

async def CompleteLeaveRequest(ctx, client, startdate, enddate, teamLead):
    if teamLead!= None:
        if ValidateDates(startdate, enddate):
            if CheckAvailableLeaves(startdate, enddate) >= 0 :
                await ctx.send(content= GetCaption(1))
                embed= CreateAnnualLeaveEmbed(ctx= ctx, startdate= startdate, enddate= enddate)
                message= await teamLead.send(embed=embed, components = [[approve_btn, reject_btn]])
                await HandleApprovalsButtons(ctx= ctx, client= client, message= message)

            else:
                await ctx.send(content= GetCaption(2) + str(int(os.getenv("Abdo_days"))))

        else:
            await ctx.send(content= GetCaption(3))
        
    else:
        await ctx.send(content= GetCaption(4))

# helper functions
def CreateDateChoices():
    firstDate = date.today() + timedelta(1)
    dateChoices = []
    
    for i in range(25):
        tmpDate = firstDate + timedelta(i)
        weekDay = tmpDate.strftime("%A")
        dateChoices.append(create_choice(name= weekDay +": "+ tmpDate.strftime('%m/%d/%Y'), value= tmpDate.strftime('%m/%d/%Y')))
    
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

def CheckAvailableLeaves(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    requestedDays = (eDate - sDate).days

    return int(os.getenv("Abdo_days")) - requestedDays

def ValidateDates(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    return eDate >= sDate

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
        description= GetCaption(8), 
        colour= 0xFF0000
    )

    return embed

async def ApproveLeave(author):
    await author.send(content= GetCaption(5))

async def RejectLeave(author):
    await author.send(content= GetCaption(6))

async def HandleApprovalsButtons(ctx, client, message):
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
        await ctx.author.send("Your Request has failed, try again later")

async def HandleWarningButtons(ctx, client, message, startdate, enddate, teamLead):
    if message!= None:
        def check(res):
            return res.message.id == message.id

        status = await client.wait_for("button_click", check = check)
        clickedButton = status.component.custom_id

        print(clickedButton)

        if clickedButton == "continue_btn":
            await CompleteLeaveRequest(ctx, client, startdate, enddate, teamLead)
            await status.message.delete()

        elif clickedButton == "cancel_btn":
            await status.message.delete()

    else:
        await ctx.author.send("Your Request has failed, try again later")


# to be changed to get captions from DB 
def GetCaption(captionCode):
    switcher = {
        1: "Your Annual leave request has been sent",
        2: "You dont have enough leaves to request you current balance is ",
        3: "Please select valid dates",
        4: "Your Request has failed, try again later",
        5: "Your annual leave request was approved",
        6: "Your annual leave request was rejected",
        7: "Your request is being processed",
        8: "It is past core hours you leave request with be considered as an emergency leave"
    }

    return switcher.get(captionCode, lambda: "Invalid caption code")