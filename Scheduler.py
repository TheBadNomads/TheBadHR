import os
import UI

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

def Setup(client):
    global bot
    bot = client
    scheduler = AsyncIOScheduler(timezone = "Africa/Cairo")
    AddSchedulerJobs(scheduler)
    scheduler.start()

def AddSchedulerJobs(scheduler):
    scheduler.add_job(GetEndofMonthReport, "cron", day = int(os.getenv("End_of_Month_Report_Day")), hour = int(os.getenv("End_of_Month_Report_hour")), minute = int(os.getenv("End_of_Month_Report_minute")))
    scheduler.add_job(GetEndofYearReport, "cron", month = int(os.getenv("End_of_Year_Report_Month")), day = int(os.getenv("End_of_Year_Report_Day")), hour = int(os.getenv("End_of_Year_Report_hour")), minute = int(os.getenv("End_of_Year_Report_minute")))
    # add more jobs here

async def GetEndofMonthReport():
    finance_admin = await bot.fetch_user(int(os.getenv("Finance_Admin_id")))
    embed = UI.CreateGetEndOfMonthReportEmbed()
    await finance_admin.send(embed = embed)

async def GetEndofYearReport():
    finance_admin = await bot.fetch_user(int(os.getenv("Finance_Admin_id")))
    embed = UI.CreateGetEndOfYearReportEmbed()
    await finance_admin.send(embed = embed)
