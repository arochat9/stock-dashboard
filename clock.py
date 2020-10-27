from app import createTickerDict, testMethod
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
import datetime

# Here is the cron job so that the table can update once a day
scheduler = BackgroundScheduler(daemon=True)
@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=3, minute=45, timezone='UTC')
def scheduled_job():
    print("**********")
    print("inside cron job")
    print("**********")
    app.testMethod("in Test Method!!!")
    # createTickerDict('compilation.csv')
scheduler.start()
