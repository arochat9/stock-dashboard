from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date
import datetime
import pandas as pd
import requests #FOR keeping the app awake
import pytz
# from data import settimeOfLastUpdate
import json #FOR JSON files
import psycopg2 #For progres database
# import sqlalchemy #For working with database
from worker import createTickerDict, enterElement
EST = pytz.timezone('America/New_York')

# createTickerDict('compilation_testSize.csv')
print("started clock.py")
# Here is the cron job so that the table can update once a day
scheduler = BackgroundScheduler(daemon=True)
@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=0, minute=15, timezone='UTC')
def scheduled_job():
    print("**********")
    print("inside cron job")
    print("**********")
    createTickerDict('compilation.csv')
# @scheduler.scheduled_job('interval', minutes=1)
# def test():
#     print("**********")
#     print("inside cron job number 2")
#     print("**********")
#
#     today1 = datetime.datetime.now(EST).strftime("%Y-%m-%d %I:%M %p")
#     enterElement(today1, 15)
#     # settimeOfLastUpdate(today1)
#     # with open("JSON Files/datetime.txt", "w+") as f:
#     #     f.write(today1)
#     # # pickle.dump(today1, open('pickleFiles/datetimeNEW','wb') )
#     # print('completed pickle time dump')
#     createTickerDict('compilation.csv')

scheduler.start()

sched = BlockingScheduler()
# scheduler = BlockingScheduler()
@sched.scheduled_job('interval', minutes=2)
def timed_job():
    # terminateConnections()
    print('This job is run every minute')
    timeNow = datetime.datetime.now(EST)
    timeNow = timeNow.strftime("%H:%M")
    timeNow = datetime.datetime.strptime(timeNow, "%H:%M")
    timeStart = '2:00PM'
    timeEnd = '4:00PM'
    timeEnd = datetime.datetime.strptime(timeEnd, "%I:%M%p")
    timeStart = datetime.datetime.strptime(timeStart, "%I:%M%p")
    print(timeNow)
    print(timeStart)
    print(timeEnd)
    if timeNow > timeStart and timeNow < timeEnd:
        print('In downtime window')
    else:
        response = requests.get('https://my-stock-dashboard-app.herokuapp.com/')
        print(response)

sched.start()

# while True:
#     pass
