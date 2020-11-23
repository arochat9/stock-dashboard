from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import requests #FOR keeping the app awake
import pytz
from worker import createTickerDict, enterElement
import time
import sys
EST = pytz.timezone('America/New_York')

# createTickerDict('compilation_testSize.csv')
print("started clock.py")

# Here is the cron job so that the table can update once a day
scheduler = BackgroundScheduler(daemon=True)
@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=22, minute=30, timezone='UTC') #run at 5:30 est
def scheduled_job():
    print("**********")
    print("inside cron job")
    print("**********")
    createTickerDict('compilation.csv')

scheduler.start()

sched = BlockingScheduler()
@sched.scheduled_job('cron', day_of_week='mon-fri', hour=22, minute=28, timezone='UTC') #run at 5:30 est
def scheduled_job():
    print('ABOUT TO START PULL')

# @sched.scheduled_job('interval', minutes=20)
# def timed_job():
#     # terminateConnections()
#     print('This job is run every 9 minutes')
#     timeNow = datetime.datetime.now(EST)
#     timeNow = timeNow.strftime("%H:%M")
#     timeNow = datetime.datetime.strptime(timeNow, "%H:%M")
#     timeStart = '1:00AM'
#     timeEnd = '10:00AM'
#     timeEnd = datetime.datetime.strptime(timeEnd, "%I:%M%p")
#     timeStart = datetime.datetime.strptime(timeStart, "%I:%M%p")
#     print(timeNow)
#     print(timeStart)
#     print(timeEnd)
#     if timeNow > timeStart and timeNow < timeEnd:
#         print('In downtime window')
#     else:
#
#         try:
#             time.sleep(1)
#             response = requests.get('https://my-stock-dashboard-app.herokuapp.com/')
#             time.sleep(1)
#             print(response)
#         except:
#             e = sys.exc_info()[0]
#             print(e)
#         else:
#             print('1good!')

sched.start()
createTickerDict('compilation.csv')
