# from app import createTickerDict, testMethod
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
import datetime
from contextlib import contextmanager
import sys, os
from tqdm import tqdm
import pickle
import pandas as pd
import yfinance as yf

marketSize_list = ['Total Market', 'Only ETFs', 'Only Fortune 500']
timeLength_list = ['1 Day', '1 Week', '1 Month', '1 Year']

#To supress print lines from yfinance
@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

#organizes data to see percent change for different stocks
def getMarketMoverData(category, timeLength, data1, data2):
    tickers_df = data1
    ticker_df_dict = data2

    if timeLength == '1 Day':
        timeIndex = -1
    elif timeLength == '1 Week':
        timeIndex = -5
    elif timeLength == '1 Month':
        timeIndex = -24
    else:
        timeIndex = 1

    temp_df = tickers_df
    if category=="Only ETFs":
        temp_df = tickers_df.loc[tickers_df['ETF'] == 'Y']
    elif category == "Only Fortune 500":
        temp_df = tickers_df.loc[tickers_df['Fortune 500'] == 'Y']

    table_list = []
    for tickerString in temp_df['Symbol'].to_list():
        ticker_df=ticker_df_dict.get(tickerString, pd.DataFrame({'A' : []}))
        if(ticker_df.empty):
            continue;
        # print(ticker_df)
        if abs(timeIndex) >= len(ticker_df.index):
            if ticker_df['Open'].iloc[0] == 0.0:
                continue
            percentChange = (ticker_df['Adj Close'].iloc[-1]/ticker_df['Open'].iloc[0]-1)*100
        else:
            percentChange = (ticker_df['Adj Close'].iloc[-1]/ticker_df['Open'].iloc[timeIndex]-1)*100

        if pd.isna(percentChange) == False:
            percentChange = round(percentChange, 2)
            volume = "{:,}".format(int(ticker_df['Volume'].iloc[-1]))
            tempList = [tickerString, percentChange, round(ticker_df['Adj Close'].iloc[-1],2), volume]
            table_list.append(tempList)

    return pd.DataFrame(table_list, columns=['Symbol', '% Change', 'Price', 'Volume'])

#Calls getMarketMoverData for all different possible parameters
def getEverythingFromMarketMover(tickers_df,ticker_df_dict):
    print("Creating market mover data")
    marketMoverData_dict = {}
    for marketSize in marketSize_list:
        for timeLength in timeLength_list:
            marketMoverData_dict[(marketSize,timeLength)] = getMarketMoverData(marketSize,timeLength, tickers_df,ticker_df_dict)
    print("Finished creating market mover data")
    pickle.dump(marketMoverData_dict, open("pickleFiles/marketMoverData_dict.p", "wb" ), protocol=-1)

def createTickerDict(filename):
    # tickers_df = pickle.load( open("pickleFiles/tickers_df full.p", "rb") )
    # ticker_df_dict = pickle.load( open("pickleFiles/ticker_df_dict full.p", "rb") )
    # getEverythingFromMarketMover(tickers_df,ticker_df_dict)
    # return

    print("Beginning yfinance data pull")

    tickers_df = pd.read_csv('Tickers/'+filename)
    # tickerStrings = tickers_df['Symbol'].to_list()
    size = 500
    list_of_dfs = [tickers_df.loc[i:i+size-1,:] for i in range(0, len(tickers_df),size)]
    ticker_df_dict_temp = {}
    count = 1
    temp_tickers_df = pd.DataFrame({'A' : []})
    for df in list_of_dfs:
        for ticker in df['Symbol'].to_list():
            try:
                with suppress_stdout():
                    data = yf.download(ticker, group_by="Ticker", period='1y')
                ticker_df_dict_temp[ticker] = data
            except Exception as ex:
                print(ex)
                continue
        print("Completed Section.")
        print("Finished "+str(500*count)+" Tickers so far")
        if (temp_tickers_df.empty):
            temp_tickers_df = df
        else:
            temp_tickers_df = temp_tickers_df.append(df)

        if (count % 2) == 0:
            getEverythingFromMarketMover(temp_tickers_df,ticker_df_dict_temp)
        count = count + 1
        pickle.dump(temp_tickers_df, open("pickleFiles/tickers_df.p", "wb" ), protocol=-1)
        today1 = datetime.datetime.today().strftime("%Y-%m-%d %I:%M %p")
        pickle.dump(today1, open('pickleFiles/datetime','wb') )
        # pickle.dump(ticker_df_dict_temp, open("pickleFiles/ticker_df_dict.p", "wb" ), protocol=-1)

    print("Completed yfinance data pull")

    ticker_df_dict = ticker_df_dict_temp
    getEverythingFromMarketMover(tickers_df,ticker_df_dict)
    pickle.dump(tickers_df, open("pickleFiles/tickers_df.p", "wb" ), protocol=-1)
    today1 = datetime.datetime.today().strftime("%Y-%m-%d %I:%M %p")
    pickle.dump(today1, open('pickleFiles/datetime','wb') )
    # pickle.dump(ticker_df_dict, open("pickleFiles/ticker_df_dict.p", "wb" ), protocol=-1)

# Here is the cron job so that the table can update once a day
scheduler = BackgroundScheduler()
@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=5, minute=18, timezone='UTC')
def scheduled_job():
    print("**********")
    print("inside cron job")
    print("**********")
    # createTickerDict('compilation.csv')

@scheduler.scheduled_job('interval', minutes=1)
def timed_job():
    print('This job is run every  minute.')

def startScheduler():
    scheduler.start()

# while True:
#     pass
