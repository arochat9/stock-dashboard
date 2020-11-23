import requests
import time
import pytz
import datetime
EST = pytz.timezone('America/New_York')

def pingWebsite():
    # terminateConnections()
    print('This job is run every 10 minutes')
    timeNow = datetime.datetime.now(EST)
    timeNow = timeNow.strftime("%H:%M")
    timeNow = datetime.datetime.strptime(timeNow, "%H:%M")
    timeStart = datetime.datetime.strptime('1:00AM', "%I:%M%p")
    timeEnd = datetime.datetime.strptime('10:00AM', "%I:%M%p")
    print(timeNow)
    print(timeStart)
    print(timeEnd)
    if timeNow > timeStart and timeNow < timeEnd:
        print('Currently In downtime window')
    else:

        try:
            time.sleep(1)
            response = requests.get('https://my-stock-dashboard-app.herokuapp.com/')
            time.sleep(1)
            print(response)
        except:
            e = sys.exc_info()[0]
            print('error on website ping')
            print(e)
            print('printed error')
        else:
            print('Ping worked')

pingWebsite()
