import discord
import os
import UI

from datetime import date, timedelta, datetime
from discord_components import DiscordComponents, Button, Select, SelectOption
from discord_components.component import ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice

# global vars
approve_btn = UI.CreateApproveButton()
reject_btn = UI.CreateRejectButton()

continue_btn = UI.CreateContinueButton()
cancel_btn = UI.CreateCancelButton()

async def RequestLeave(ctx, client, leavetype, startdate, enddate):
    leavesChannel = await client.get_channel(int(os.getenv("TestChannel_id")))

    leaveFunctions = {
        "annual"   : RequestAnnualLeave,
        "emergency": RequestEmergencyLeave,
        "sick"     : RequestSickLeave
    }

    await leaveFunctions[leavetype](ctx, client, startdate, enddate, leavesChannel)

async def RequestAnnualLeave(ctx, client, startdate, enddate, leavesChannel):
    current_time = datetime.now().hour
    if ValidateDates(startdate, enddate):
        if CheckAvailableBalance(startdate, enddate, "annual"):
            if current_time > 12:
                await SendWarningMessage(ctx, client, startdate, enddate, leavesChannel)
            else:
                await ctx.send(content = UI.GetCaption(1))
                embed = UI.CreateAnnualLeaveEmbed(ctx, startdate, enddate)
                message = await leavesChannel.send(embed = embed, components = [[approve_btn, reject_btn]])
                await UI.HandleApprovalsButtons(ctx, client, message, "annual")

        else:
            await ctx.send(content = UI.GetCaption(2) + str(int(os.getenv("Abdo_Annual_Leaves"))))

    else:
        await ctx.send(content = UI.GetCaption(3))

async def RequestEmergencyLeave(ctx, client, startdate, enddate, leavesChannel):
    if ValidateDates(startdate, enddate):
        if CheckAvailableBalance(startdate, enddate, "emergency"):
            await ctx.send(content = UI.GetCaption(1))
            embed = UI.CreateEmergencyLeaveEmbed(ctx, startdate, enddate)
            message = await leavesChannel.send(embed = embed, components = [[approve_btn, reject_btn]])
            await UI.HandleApprovalsButtons(ctx, client , message, "emergency")

        else:
            await ctx.send(content = UI.GetCaption(2) + str(int(os.getenv("Abdo_Emergency_Leaves"))))

    else:
        await ctx.send(content = UI.GetCaption(3))

async def RequestSickLeave(ctx, client, startdate, enddate, leavesChannel):
    if ValidateDates(startdate, enddate):
        if CheckAvailableBalance(startdate, enddate, "sick"):
            await ctx.send(content = UI.GetCaption(1))
            embed = UI.CreateSickLeaveEmbed(ctx, startdate, enddate)
            message = await leavesChannel.send(embed = embed, components = [[approve_btn, reject_btn]])
            await UI.HandleApprovalsButtons(ctx, client, message, "sick")

        else:
            await ctx.send(content = UI.GetCaption(2) + str(int(os.getenv("Abdo_Sick_Leaves"))))

    else:
        await ctx.send(content = UI.GetCaption(3))
    
async def SendWarningMessage(ctx, client, startdate, enddate, leavesChannel):
    await ctx.send(content = UI.GetCaption(7))
    message = await ctx.author.send(embed = UI.CreateWarningEmbed(), components = [[continue_btn, cancel_btn]])
    await UI.HandleWarningButtons(ctx, client, message, startdate, enddate, leavesChannel)

# helper functions
def CheckAvailableBalance(startdate: str, enddate: str, leavetype: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    requestedDays = (eDate - sDate).days + 1

    returnValues = {
        "annual"   : int(os.getenv("Abdo_Annual_Leaves")) - requestedDays,
        "emergency": int(os.getenv("Abdo_Emergency_Leaves")) - requestedDays,
        "sick"     : int(os.getenv("Abdo_Sick_Leaves")) - requestedDays
    }

    return returnValues[leavetype] >= 0

def ValidateDates(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    return eDate >= sDate
