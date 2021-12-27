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
    print("add jobs here")
    # add more jobs here