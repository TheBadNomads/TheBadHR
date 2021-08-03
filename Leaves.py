import discord
import os

from datetime import date, timedelta, datetime
from discord_components import DiscordComponents, Button, Select, SelectOption
from discord_components.component import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice

# global vars
approve_btn= Button(label= 'Approve', style= ButtonStyle.green, custom_id= 'approve_btn')
reject_btn= Button(label= 'Reject', style= ButtonStyle.red, custom_id= 'reject_btn')

continue_btn= Button(label= 'Continue', style= ButtonStyle.gray, custom_id= 'continue_btn')
cancel_btn= Button(label= 'Cancel', style= ButtonStyle.red, custom_id= 'cancel_btn')

async def RequestAnnualLeave(ctx, client, startdate, enddate, teamLead):
    if teamLead!= None:
        if ValidateDates(startdate, enddate):
            if CheckAvailableLeaves(startdate, enddate, "annual") >= 0 :
                await ctx.send(content= GetCaption(1))
                embed= CreateAnnualLeaveEmbed(ctx= ctx, startdate= startdate, enddate= enddate)
                message= await teamLead.send(embed= embed, components= [[approve_btn, reject_btn]])
                await HandleApprovalsButtons(ctx= ctx, client= client, message= message, leavetype= "annual")

            else:
                await ctx.send(content= GetCaption(2) + str(int(os.getenv("Abdo_Annual_Leaves"))))

        else:
            await ctx.send(content= GetCaption(3))
        
    else:
        await ctx.send(content= GetCaption(4))

async def RequestEmergencyLeave(ctx, client, startdate, enddate, teamLead):
    if teamLead!= None:
        if ValidateDates(startdate, enddate):
            if CheckAvailableLeaves(startdate, enddate, "emergency") >= 0 :
                await ctx.send(content= GetCaption(1))
                embed= CreateEmergencyLeaveEmbed(ctx= ctx, startdate= startdate, enddate= enddate)
                message= await teamLead.send(embed= embed, components= [[approve_btn, reject_btn]])
                await HandleApprovalsButtons(ctx= ctx, client= client, message= message, leavetype= "emergency")

            else:
                await ctx.send(content= GetCaption(2) + str(int(os.getenv("Abdo_Emergency_Leaves"))))

        else:
            await ctx.send(content= GetCaption(3))
        
    else:
        await ctx.send(content= GetCaption(4))

async def RequestSickLeave(ctx, client, startdate, enddate, teamLead):
    if teamLead!= None:
        if ValidateDates(startdate, enddate):
            if CheckAvailableLeaves(startdate, enddate, "sick") >= 0 :
                await ctx.send(content= GetCaption(1))
                embed= CreateSickLeaveEmbed(ctx= ctx, startdate= startdate, enddate= enddate)
                message= await teamLead.send(embed= embed, components= [[approve_btn, reject_btn]])
                await HandleApprovalsButtons(ctx= ctx, client= client, message= message, leavetype= "sick")

            else:
                await ctx.send(content= GetCaption(2) + str(int(os.getenv("Abdo_Sick_Leaves"))))

        else:
            await ctx.send(content= GetCaption(3))
        
    else:
        await ctx.send(content= GetCaption(4))
    
async def SendWarningMessage(ctx, client, startdate, enddate, teamLead):
    await ctx.send(content= GetCaption(7))
    message= await ctx.author.send(embed= CreateWarningEmbed(), components= [[continue_btn, cancel_btn]])
    await HandleWarningButtons(ctx= ctx, client= client, message= message, startdate= startdate, enddate= enddate, teamLead= teamLead)

# helper functions
def CreateLeaveTypeChoices():
    leaveTypeChoices = []
    leaveTypeChoices.append(create_choice(name= "Annual", value= "annual"))
    leaveTypeChoices.append(create_choice(name= "Emergency", value= "emergency"))
    leaveTypeChoices.append(create_choice(name= "Sick", value= "sick"))

    return leaveTypeChoices

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
            name= "leavetype",
            description= "leave type",
            option_type= 3,
            required= True,
            choices= CreateLeaveTypeChoices()
        ),
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

def CheckAvailableLeaves(startdate: str, enddate: str, leavetype: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    requestedDays = (eDate - sDate).days

    if leavetype == "annual":
        return int(os.getenv("Abdo_Annual_Leaves")) - requestedDays

    elif leavetype == "emergency":
        return int(os.getenv("Abdo_Emergency_Leaves")) - requestedDays

    elif leavetype == "sick":
        return int(os.getenv("Abdo_Sick_Leaves")) - requestedDays
        
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

def CreateEmergencyLeaveEmbed(ctx, startdate, enddate):
    embed = discord.Embed(
        title= "Emergency Leave Request", 
        description= f'{ctx.author.mention} is requesting a leave', 
        colour= 0x4682B4
    )
    embed.set_thumbnail(url= os.getenv("Emergency_Leave_Link"))
    embed.add_field(name= "Start Date", value= startdate, inline= True)
    embed.add_field(name= "End Date", value= enddate, inline= True)
    embed.set_footer(text = date.today())

    return embed

def CreateSickLeaveEmbed(ctx, startdate, enddate):
    embed = discord.Embed(
        title= "Sick Leave Request", 
        description= f'{ctx.author.mention} is requesting a leave', 
        colour= 0x4682B4
    )
    embed.set_thumbnail(url= os.getenv("Sick_Leave_Link"))
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

async def ApproveLeave(author, leavetype):
    if leavetype == "annual":  
        await author.send(content= GetCaption(5))
    elif leavetype == "emergency":
        await author.send(content= GetCaption(9))
    elif leavetype == "sick":
        await author.send(content= GetCaption(11))

async def RejectLeave(author, leavetype):
    if leavetype == "annual":  
        await author.send(content= GetCaption(6))
    elif leavetype == "emergency":
        await author.send(content= GetCaption(10))
    elif leavetype == "sick":
        await author.send(content= GetCaption(12))

async def HandleApprovalsButtons(ctx, client, message, leavetype):
    if message != None:
        def check(res):
            return res.message.id == message.id

        status = await client.wait_for("button_click", check = check)
        clickedButton = status.component.custom_id

        if clickedButton == "approve_btn":
            await status.respond(content = "The request has been approved")
            await ApproveLeave(ctx.author, leavetype)

        elif clickedButton == "reject_btn":
            await status.respond(content = "The request has been rejected")
            await RejectLeave(ctx.author, leavetype)
            
    else:
        await ctx.author.send("Your Request has failed, try again later")

async def HandleWarningButtons(ctx, client, message, startdate, enddate, teamLead):
    if message!= None:
        def check(res):
            return res.message.id == message.id

        status = await client.wait_for("button_click", check = check)
        clickedButton = status.component.custom_id

        if clickedButton == "continue_btn":
            await status.message.delete()
            await RequestEmergencyLeave(ctx, client, startdate, enddate, teamLead)

        elif clickedButton == "cancel_btn":
            await status.message.delete()

    else:
        await ctx.author.send("Your Request has failed, try again later")

# to be changed to get captions from DB 
def GetCaption(captionCode):
    switcher = {
        1: "Your leave request has been sent",
        2: "You dont have enough leaves to request, your current balance is ",
        3: "Please select valid dates",
        4: "Your Request has failed, try again later",
        5: "Your annual leave request was approved",
        6: "Your annual leave request was rejected",
        7: "Your request is being processed",
        8: "It is past core hours you leave request with be considered as an emergency leave",
        9: "Your emergency leave request was approved",
        10: "Your emergency leave request was rejected",
        11: "Your sick leave request was approved",
        12: "Your sick leave request was rejected",
    }

    return switcher.get(captionCode, lambda: "Invalid caption code")