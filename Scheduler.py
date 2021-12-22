import os
import UI

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from Member import member_db 

def Setup(client):
    global bot
    bot = client
    scheduler = AsyncIOScheduler(timezone = "Africa/Cairo")
    AddSchedulerJobs(scheduler)
    scheduler.start()

def AddSchedulerJobs(scheduler):
<<<<<<< HEAD
    scheduler.add_job(SendEndofMonthReport, "cron", day = int(os.getenv("End_of_Month_Report_Day")), hour = int(os.getenv("End_of_Month_Report_Hour")), minute = int(os.getenv("End_of_Month_Report_Minute")))
    scheduler.add_job(SendEndofYearReport, "cron", month = int(os.getenv("End_of_Year_Report_Month")), day = int(os.getenv("End_of_Year_Report_Day")), hour = int(os.getenv("End_of_Year_Report_Hour")), minute = int(os.getenv("End_of_Year_Report_Minute")))
=======
    scheduler.add_job(SendEndOfMonthCalculations, CronTrigger(day = 20, hour = 11, minute = 5))
    # add more jobs here
>>>>>>> c62b5f0 (replacing dumy values)

<<<<<<< HEAD
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
=======
async def SendEndOfMonthCalculations(finance_admin = None, month = None, year = None):
    month = month or datetime.now().month
    year = year or datetime.now().year
    finance_admin = finance_admin or await bot.fetch_user(int(os.getenv("Finance_Admin_id")))
    embed = UI.CreateGetEndOfMonthCalculationsEmbed(month, year)
    await finance_admin.send(embed = embed)
>>>>>>> 7ecd732 (adding newline)
