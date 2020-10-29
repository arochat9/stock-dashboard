import yfinance as yf
import matplotlib.pyplot as plt
from operator import itemgetter
import pandas as pd
import pickle
import timeit
import datetime
from sys import getsizeof
import pytz
import json
import sqlalchemy
import os
from worker import getMostRecentPull, enterElement

URL = 'postgres://rrfjatgyxoplxp:85abb6064386584979cf0d6ddb56ed5e3154d743afd18dd42e4e6c46287f9f40@ec2-18-210-90-1.compute-1.amazonaws.com:5432/d9qtfjohvv68rv'


def createTables():
    engine = sqlalchemy.create_engine(URL)
    con = engine.connect()
    # print(engine.table_names())

    with open('JSON Files/marketMoverData_dict.json') as json_file:
        data = json.load(json_file)

    for key in data.keys():
        df = pd.read_json(data[key])
        df = df.rename({'% Change': 'Percent Change'}, axis=1)  # new method
        df = df.nsmallest(10,'Percent Change').append(df.nlargest(10,'Percent Change'))
        print("key: "+str(key))
        table_name = key
        df.to_sql(table_name, con, if_exists='replace')

    print(engine.table_names())
    con.close()
    engine.dispose()
# createTables()
print("**********")

def getTopData():
    engine = sqlalchemy.create_engine("postgresql://postgres:Maroon6248@localhost/dashboard-database")
    con = engine.connect()
    var = 'Total Market-1 Day'
    dataFrame = pd.read_sql("select * from \""+var+"\"", con);
    con.close()
    return dataFrame.nsmallest(10,'Percent Change')


def table2(value="Total Market", period="1 Day"):

    engine = sqlalchemy.create_engine(URL)
    con = engine.connect()
    var = value+"-"+period
    dataFrame = pd.read_sql("select * from \""+var+"\"", con);
    con.close()
    engine.dispose()
    dataFrame['Percent Change'] = dataFrame['Percent Change'].apply(lambda x: float(x))
    dataFrame = dataFrame.nsmallest(10,'Percent Change')
    dataFrame['Percent Change'] = dataFrame['Percent Change'].apply(lambda x: round(x, 2))
    return dataFrame.to_dict("records")
    # print(dataFrame)

# table2()
number=4
timeTaken = timeit.timeit(table2, number=number)
print("AVG TIME TAKEN for method")
print(timeTaken/number)

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String, Date
# # DATABASE_URL = os.environ['postgres://rrfjatgyxoplxp:85abb6064386584979cf0d6ddb56ed5e3154d743afd18dd42e4e6c46287f9f40@ec2-18-210-90-1.compute-1.amazonaws.com:5432/d9qtfjohvv68rv']
# URL = 'postgres://rrfjatgyxoplxp:85abb6064386584979cf0d6ddb56ed5e3154d743afd18dd42e4e6c46287f9f40@ec2-18-210-90-1.compute-1.amazonaws.com:5432/d9qtfjohvv68rv'

# enterElement("testing",1)

# Base = declarative_base()
#
# class Book(Base):
#     __tablename__ = 'dashInfo_table'
#     id = Column(Integer, primary_key=True)
#     title = Column(String)
#     author = Column(String)
#     pages = Column(Integer)
#     published = Column(Date)
#
#     def __repr__(self):
#         return "<Book(title='{}', author='{}', pages={}, published={})>"\
#                 .format(self.title, self.author, self.pages, self.published)
#
# engine = create_engine(URL)
# Base.metadata.create_all(engine)

# Total Market-1 Day
# Total Market-1 Week
# Total Market-1 Month
# Total Market-1 Year
# Only ETFs-1 Day
# Only ETFs-1 Week
# Only ETFs-1 Month
# Only ETFs-1 Year
# Only Fortune 500-1 Day
# Only Fortune 500-1 Week
# Only Fortune 500-1 Month
# Only Fortune 500-1 Year






# EST = pytz.timezone('America/New_York')
# today1 = datetime.datetime.now(EST).strftime("%Y-%m-%d %I:%M %p")
# print("********")
# print(today1)
# # with open('JSON Files/datetime.json', 'w') as fp:
# #     json.dump(str(today1), fp)
# with open("JSON Files/datetime.txt", "w+") as f:
#     f.write(today1)
#
# from data import settimeOfLastUpdate, gettimeOfLastUpdate
#
# EST = pytz.timezone('America/New_York')
# today1 = datetime.datetime.now(EST).strftime("%Y-%m-%d %I:%M %p")
# settimeOfLastUpdate(today1)
#
# print(gettimeOfLastUpdate())


# dashInfo_dictSTART = {
#     'time':'not set',
#     'number':'not set',
#     'tickers':'not set'
# }
# with open('JSON Files/dashInfo_dict.json', 'w') as data:
#     json.dump(dashInfo_dictSTART, data)

# with open('JSON Files/dashInfo_dict.json', 'w') as data:
#     dashInfo_dict = data
#
# dashInfo_dict['time'] = 'new time'
# with open('JSON Files/dashInfo_dict.json', 'w') as data:
#     json.dump(dashInfo_dict, data)

# marketMoverData_dict = pickle.load( open("pickleFiles/marketMoverData_dict.p", "rb") )
#
# new_marketMoverData_dict = {}
#
# for key in marketMoverData_dict.keys():
#     print(key)
#     new_marketMoverData_dict[key[0]+"-"+key[1]] = (marketMoverData_dict.get(key)).to_json()
#
# for key in new_marketMoverData_dict.keys():
#     print(key)
#
# with open('JSON Files/marketMoverData_dict.json', 'w') as fp:
#     json.dump(new_marketMoverData_dict, fp)
#
# with open('JSON Files/marketMoverData_dict.json') as json_file:
    # data = json.load(json_file)
#     # print(data)
#
# # data = json.load('JSON Files/marketMoverData_dict.json')
#
# print(pd.read_json(data['Only ETFs-1 Day']))

# newtime = yf.download("SPY", period='1d')
# print(newtime)
# tickers_df = pd.read_csv('Tickers/compilation_testSize.csv')

# print("********")
# print(pickle.load( open("pickleFiles/ticker_df_dict.p", "rb") ))
# print("********")

# marketMoverdf = pickle.load( open("pickleFiles/marketMoverData_dict.p", "rb") )

# today1 = datetime.datetime.today().strftime("%Y-%m-%d %H:%M")
# pickle.dump(today1, open('pickleFiles/datetime','wb') )
#

# print(today1)
# today2 = pickle.load(open('pickleFiles/datetime','rb'))
# print(today2)

# print(marketMoverdf[('Total Market', '1 Day')])
# print(pickle.load( open("pickleFiles/tickers_df.p", "rb") ))

# tickers_df = pickle.load( open("pickleFiles/tickers_df full.p", "rb") )
# ticker_df_dict = pickle.load( open("pickleFiles/ticker_df_dict full.p", "rb") )

# testVarr = 1
# print("size of test var"+str(getsizeof(testVarr)))
# print("size of ticker_df_dict"+str(getsizeof(ticker_df_dict)))
#
#
# def getMarketMoverData(category, timeLength):
#
#     print("length of dict in market mover")
#     print(len(ticker_df_dict))
#     print("length of tickers in market mover")
#     print(len(tickers_df))
#
#     if timeLength == '1 Day':
#         timeIndex = -1
#     elif timeLength == '1 Week':
#         timeIndex = -5
#     elif timeLength == '1 Month':
#         timeIndex = -24
#     else:
#         timeIndex = 1
#
#     temp_df = tickers_df
#     if category=="Only ETFs":
#         temp_df = tickers_df.loc[tickers_df['ETF'] == 'Y']
#     elif category == "Only Fortune 500":
#         temp_df = tickers_df.loc[tickers_df['Fortune 500'] == 'Y']
#
#     table_list = []
#
#     for tickerString in temp_df['Symbol'].to_list():
#         ticker_df=ticker_df_dict.get(tickerString, pd.DataFrame({'A' : []}))
#         if(ticker_df.empty):
#             continue
#         # print(ticker_df)
#         if abs(timeIndex) >= len(ticker_df.index):
#             if ticker_df['Open'].iloc[0] == 0.0:
#                 continue
#             percentChange = (ticker_df['Adj Close'].iloc[-1]/ticker_df['Open'].iloc[0]-1)*100
#         else:
#             percentChange = (ticker_df['Adj Close'].iloc[-1]/ticker_df['Open'].iloc[timeIndex]-1)*100
#
#         if pd.isna(percentChange) == False:
#             percentChange = round(percentChange, 2)
#             volume = "{:,}".format(int(ticker_df['Volume'].iloc[-1]))
#             tempList = [tickerString, percentChange, round(ticker_df['Adj Close'].iloc[-1],2), volume]
#             table_list.append(tempList)
#
#     return pd.DataFrame(table_list, columns=['Symbol', '% Change', 'Price', 'Volume'])
#
# # print(getMarketMoverData("Total Market", "1 Day"))
# def wrapper():
#     temp_df = getMarketMoverData('Total Market','1 Day')
#     # print(temp_df.nlargest(10,'% Change'))
#
# def getEverything():
#     marketMoverData_dict = {}
#     for marketSize in ['Total Market', 'Only ETFs', 'Only Fortune 500']:
#         for timeLength in ['1 Day', '1 Week', '1 Month', '1 Year']:
#             marketMoverData_dict[(marketSize,timeLength)] = getMarketMoverData(marketSize,timeLength)
#
#     # return marketMoverData_dict
#     pickle.dump(marketMoverData_dict, open("pickleFiles/marketMoverData_dict.p", "wb" ), protocol=-1)
#
# getEverything()
#
# def testGetEverything():
#     marketMoverData_dict = pickle.load( open("pickleFiles/marketMoverData_dict.p", "rb") )
#     print(marketMoverData_dict[("Total Market","1 Day")])
#
# testGetEverything()
#
#
# number=4
# timeTaken = timeit.timeit(testGetEverything, number=number)
# print("AVG TIME TAKEN")
# print(timeTaken/number)





# table_df = yf.download("SPY", period='1y', group_by='ticker', threads = False)
# print(table_df)

# table_df = yf.download(tickers=tickers_df['Symbol'].to_list(), period='1d', group_by='ticker')
# print(table_df)

# tickers_df = pd.read_csv('Tickers/compilation_testSize.csv')
#
# def createTickerDict(tickerStrings):
#     ticker_df_dict_temp = {}
#     for ticker in tickerStrings:
#         try:
#             data = yf.download(ticker, group_by="Ticker", period='1y')
#             ticker_df_dict_temp[ticker] = data
#         except Exception as ex:
#             print(ex)
#             continue
#     return ticker_df_dict_temp
#
# ticker_df_dict = createTickerDict(tickers_df['Symbol'].to_list())
#
# def getMarketMoverData(category, timeLength):
#
#     if timeLength == '1 Day':
#         timeIndex = -1
#     elif timeLength == '1 Week':
#         timeIndex = -5
#     elif timeLength == '1 Month':
#         timeIndex = -24
#     else:
#         timeIndex = 1
#
#     temp_df = tickers_df
#     if category=="Only ETFs":
#         temp_df = tickers_df.loc[tickers_df['ETF'] == 'Y']
#     elif category == "Only Fortune 500":
#         temp_df = tickers_df.loc[tickers_df['Fortune 500'] == 'Y']
#
#     table_list = []
#     for tickerString in temp_df['Symbol'].to_list():
#         ticker_df=ticker_df_dict.get(tickerString)
#         if(ticker_df == None):
#             break
#         percentChange = (ticker_df['Adj Close'].iloc[-1]/ticker_df['Open'].iloc[timeIndex]-1)*100
#         if pd.isna(percentChange) == False:
#             percentChange = round(percentChange, 2)
#             volume = "{:,}".format(int(ticker_df[column]['Volume'].iloc[-1]))
#             tempList = [column, percentChange, round(ticker_df[column]['Adj Close'].iloc[-1],2), volume]
#             table_list.append(tempList)
#
#     return pd.DataFrame(table_list, columns=['Symbol', '% Change', 'Price', 'Volume'])


# print("********")
# data = yf.download("SPY", period = '1d', threads=False)
# data.columns=['SPY']
# tickers = ['AAPL', 'MSFT']
# close_data = data.reset_index()
# for x in tickers:
#     while True:
#         try:
#             data = yf.download(x, period = '1d', threads = False)
#             # data = data.drop(columns = ['Low','High', 'Open', 'Adj Close', 'Volume'])
#             data.columns=[x]
#             data = data.reset_index()
#             stock_data=data[x]
#             close_data = pd.concat([close_data,stock_data], axis=1)
#             print(x)
#         except Exception as ex:
#             print(ex)
#             continue
#         break
# print('close_data')


# df.loc[df['ETF'] == some_value]
#
# timeLength = "1 Week"
# total_table_list = []
# etf_table_list = []
# fortune500_table_list = []
# for index, row in tickers_df.iterrows():
#
#     print('hello')
#     column = row['Symbol']
#
#     if timeLength == "1 Day":
#         percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-1]-1)*100
#     elif timeLength == "1 Week":
#         percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-7]-1)*100
#     elif timeLength == "1 Month":
#         percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-30]-1)*100
#     else:
#         percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[1]-1)*100
#
#     if pd.isna(percentChange) == False:
#         tempList = [column, percentChange, table_df[column]['Adj Close'].iloc[-1], table_df[column]['Volume'].iloc[-1]]
#         # print(tempList)
#         if (row['ETF'] == 'Y'): #TODO
#             etf_table_list.append(tempList)
#         if (row['Fortune 500'] == 'Y'): #TODO
#             fortune500_table_list.append(tempList)
#         total_table_list.append(tempList)
#
# market_df = pd.DataFrame(total_table_list, columns=['Symbol', '% Change', 'Price', 'Volume'])
# fortune500_df = pd.DataFrame(fortune500_table_list, columns=['Symbol', '% Change', 'Price', 'Volume'])
# etf_df = pd.DataFrame(etf_table_list, columns=['Symbol', '% Change', 'Price', 'Volume'])
#
#
#
# # print(total_table_list)
# marketMovers = sorted(total_table_list, key = itemgetter(1), reverse = True)
# marketMovers_Fortune500 = sorted(fortune500_table_list, key = itemgetter(1), reverse = True)
# marketMovers_etfs = sorted(etf_table_list, key = itemgetter(1), reverse = True)
# printing result

# print("***********")
# print("***********")
# print("market movers")
# for i in marketMovers:
#     print(i)
#
# print("***********")
# print("***********")
# print("fortune 500")
# for i in marketMovers_Fortune500:
#     print(i)
#
# print("***********")
# print("***********")
# print("ETFs")
# for i in marketMovers_etfs:
#     print(i)
#
# print("***********")
# print("***********")
# print("top 10 from total")
# for i in marketMovers[:10]:
#     print(i)
#
# print("***********")
# print("***********")
# print("bottom 10 from total")
# marketMovers.reverse()
# for i in marketMovers[:10]:
#     print(i)
#
# print("***********")
# print("***********")
# print("top 10 from total with DF")
# # print(market_df['Symbol'].astype(str).astype(float).nlargest(10))
# print(market_df.nlargest(10,'% Change'))
#
# print("***********")
# print("***********")
# print("Bottom 10 from total with DF")
# # print(market_df['Symbol'].astype(str).astype(float).nsmallest(10))
# print(market_df.nsmallest(10,'% Change'))
