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
    scheduler.add_job(SendEndOfMonthCalculations, "cron", day = 20, hour = 11, minute = 5)
    # add more jobs here

async def SendEndOfMonthCalculations(finance_admin = None, month = None, year = None):
    month = month or datetime.now().month
    year = year or datetime.now().year
    finance_admin = finance_admin or await bot.fetch_user(int(os.getenv("Finance_Admin_id")))
    embed = UI.CreateGetEndOfMonthCalculationsEmbed(month, year)
    await finance_admin.send(embed = embed)
