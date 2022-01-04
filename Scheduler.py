import os
import UI

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Member import member_db 

def Setup(client):
    global bot
    bot = client
    scheduler = AsyncIOScheduler(timezone = "Africa/Cairo")
    AddSchedulerJobs(scheduler)
    scheduler.start()

def AddSchedulerJobs(scheduler):
    scheduler.add_job(SendEndofMonthReport, "cron", day = int(os.getenv("End_of_Month_Report_Day")), hour = int(os.getenv("End_of_Month_Report_Hour")), minute = int(os.getenv("End_of_Month_Report_Minute")))
    scheduler.add_job(SendEndofYearReport, "cron", month = int(os.getenv("End_of_Year_Report_Month")), day = int(os.getenv("End_of_Year_Report_Day")), hour = int(os.getenv("End_of_Year_Report_Hour")), minute = int(os.getenv("End_of_Year_Report_Minute")))

async def SendEndofMonthReport():
    finance_admins_ids = os.getenv("Finance_Admins_ids").split(", ")
    embed = UI.CreateGetEndOfMonthReportEmbed(member_db.GetMembers())
    for id in finance_admins_ids:
        admin = await bot.fetch_user(int(id))
        await admin.send(embed = embed)

async def SendEndofYearReport():
    finance_admins_ids = os.getenv("Finance_Admins_ids").split(", ")
    embed = UI.CreateGetEndOfYearReportEmbed(member_db.GetMembers())
    for id in finance_admins_ids:
        admin = await bot.fetch_user(int(id))
        await admin.send(embed = embed)
