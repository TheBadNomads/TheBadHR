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
    scheduler.add_job(SendEndOfMonthCalculations, "cron", day = int(os.getenv("End_of_Month_Report_Day")), hour = int(os.getenv("End_of_Month_Report_hour")), minute = int(os.getenv("End_of_Month_Report_minute")))
    # add more jobs here

async def SendEndOfMonthCalculations(finance_admin = None, month = None, year = None):
    month = month or datetime.now().month
    year = year or datetime.now().year
    finance_admin = finance_admin or await bot.fetch_user(int(os.getenv("Finance_Admin_id")))
    embed = UI.CreateGetEndOfMonthCalculationsEmbed(month, year)
    await finance_admin.send(embed = embed)
