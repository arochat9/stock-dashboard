from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime
import requests #FOR keeping the app awake
import pytz
from worker import createTickerDict, enterElement

EST = pytz.timezone('America/New_York')

# createTickerDict('compilation_testSize.csv')
print("started clock.py")

# Here is the cron job so that the table can update once a day
scheduler = BackgroundScheduler(daemon=True)
@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=21, minute=30, timezone='UTC') #run at 5:30 est
def scheduled_job():
    print("**********")
    print("inside cron job")
    print("**********")
    createTickerDict('compilation.csv')

scheduler.start()

sched = BlockingScheduler()
# scheduler = BlockingScheduler()
@sched.scheduled_job('interval', minutes=20)
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
