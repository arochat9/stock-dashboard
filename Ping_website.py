import requests
import time

def pingWebsite():
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
