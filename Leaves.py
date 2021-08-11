import discord
import os
import UI

from datetime import date, timedelta, datetime

# global vars

async def RequestLeave(ctx, client, leavetype, startdate, enddate, leavesChannel):
    current_time = datetime.now().hour
    embeds = {
        1: UI.CreateAnnualLeaveEmbed,
        2: UI.CreateEmergencyLeaveEmbed,
        3: UI.CreateSickLeaveEmbed
    }

    if ValidateDates(startdate, enddate):
        if CheckAvailableBalance(startdate, enddate, leavetype):
            if current_time < 12:
                await SendWarningMessage(ctx, client, startdate, enddate, leavesChannel)
            else:
                await ctx.send(content = UI.GetCaption(1))
                embed = embeds[leavetype](ctx, startdate, enddate)
                message = await leavesChannel.send(embed = embed)
                await message.add_reaction("✅")
                await message.add_reaction("❌")

        else:
            await ctx.send(content = UI.GetCaption(2) + str(int(os.getenv("Abdo_Annual_Leaves"))))

    else:
        await ctx.send(content = UI.GetCaption(3))

async def SendWarningMessage(ctx, client, startdate, enddate, leavesChannel):
    await ctx.send(content = UI.GetCaption(7))
    message = await ctx.author.send(embed = UI.CreateWarningEmbed())
    continue_pressed = await UI.HandleWarningButtons(ctx, client, message, startdate, enddate, leavesChannel)
    
    if continue_pressed:
        RequestLeave(ctx, client, "emergency", startdate, enddate, leavesChannel)

# helper functions
def CheckAvailableBalance(startdate: str, enddate: str, leavetype: str):
    requestedDays = GetRequestedDays(startdate, enddate)

    returnValues = {
        1: int(os.getenv("Abdo_Annual_Leaves")) - requestedDays,
        2: int(os.getenv("Abdo_Emergency_Leaves")) - requestedDays,
        3: int(os.getenv("Abdo_Sick_Leaves")) - requestedDays
    }

    return returnValues[leavetype] >= 0

def GetRequestedDays(startdate: str, enddate: str,):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    total_days = []

    for i in range((eDate - sDate).days + 1):
        day = sDate + timedelta(days=i)
        if day.weekday() != 4 and day.weekday() != 5:
            total_days.append(day) 

    return len(total_days)

def ValidateDates(startdate: str, enddate: str):
    sDate = datetime.strptime(startdate, '%m/%d/%Y')
    eDate = datetime.strptime(enddate, '%m/%d/%Y')

    return eDate >= sDate
