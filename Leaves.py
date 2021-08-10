import discord
import os
import UI

from datetime import date, timedelta, datetime

# global vars
approve_btn = UI.CreateApproveButton()
reject_btn = UI.CreateRejectButton()

continue_btn = UI.CreateContinueButton()
cancel_btn = UI.CreateCancelButton()

async def RequestLeave(ctx, client, leavetype, startdate, enddate, leavesChannel):
    
    current_time = datetime.now().hour

    embeds = {
        "annual"   : UI.CreateAnnualLeaveEmbed,
        "emergency": UI.CreateEmergencyLeaveEmbed,
        "sick"     : UI.CreateSickLeaveEmbed
    }

    if ValidateDates(startdate, enddate):
        if CheckAvailableBalance(startdate, enddate, leavetype):
            if current_time > 12:
                await SendWarningMessage(ctx, client, startdate, enddate, leavesChannel)
            else:
                await ctx.send(content = UI.GetCaption(1))
                embed = embeds[leavetype](ctx, startdate, enddate)
                message = await leavesChannel.send(embed = embed, components = [[approve_btn, reject_btn]])
                await UI.HandleApprovalsButtons(ctx, client, message, leavetype)

        else:
            await ctx.send(content = UI.GetCaption(2) + str(int(os.getenv("Abdo_Annual_Leaves"))))

    else:
        await ctx.send(content = UI.GetCaption(3))

async def SendWarningMessage(ctx, client, startdate, enddate, leavesChannel):
    await ctx.send(content = UI.GetCaption(7))
    message = await ctx.author.send(embed = UI.CreateWarningEmbed(), components = [[continue_btn, cancel_btn]])
    continue_pressed = await UI.HandleWarningButtons(ctx, client, message, startdate, enddate, leavesChannel)
    
    if continue_pressed:
        RequestLeave(ctx, client, "emergency", startdate, enddate, leavesChannel)


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
