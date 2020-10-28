import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import pandas as pd # used for dataframes
import pytz # used to find timezone for datetime
import datetime # used for today1 variable
import sys, os
import yfinance as yf

marketSize_list = ['Total Market', 'Only ETFs', 'Only Fortune 500']
timeLength_list = ['1 Day', '1 Week', '1 Month', '1 Year']
EST = pytz.timezone('America/New_York')
# URL = "postgresql://postgres:Maroon6248@localhost/dashboard-database"
URL = 'postgres://rrfjatgyxoplxp:85abb6064386584979cf0d6ddb56ed5e3154d743afd18dd42e4e6c46287f9f40@ec2-18-210-90-1.compute-1.amazonaws.com:5432/d9qtfjohvv68rv'
# DATABASE_URL = os.environ['postgres://rrfjatgyxoplxp:85abb6064386584979cf0d6ddb56ed5e3154d743afd18dd42e4e6c46287f9f40@ec2-18-210-90-1.compute-1.amazonaws.com:5432/d9qtfjohvv68rv']
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
#postgres://rrfjatgyxoplxp:85abb6064386584979cf0d6ddb56ed5e3154d743afd18dd42e4e6c46287f9f40@ec2-18-210-90-1.compute-1.amazonaws.com:5432/d9qtfjohvv68rv

Base = declarative_base()
class dashInfo(Base):
    __tablename__ = 'dashInfo_table'
    time = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    amount = sqlalchemy.Column(sqlalchemy.SmallInteger)

    def __repr__(self):
        return "Currently have {} out of 9211 stocks loaded. Last pull: {} EST".format(self.amount, self.time)

# def recreate_database():
#     Base.metadata.drop_all(engine)
#     Base.metadata.create_all(engine)

def terminateConnections():
    engine = sqlalchemy.create_engine(URL)
    conn = engine.connect()
    cur = conn.cursor()
    cur.callproc('function_name', (value1,value2))
    cur.execute("""
    WITH inactive_connections AS (
        SELECT
            pid,
            rank() over (partition by client_addr order by backend_start ASC) as rank
        FROM
            pg_stat_activity
        WHERE
            -- Exclude the thread owned connection (ie no auto-kill)
            pid <> pg_backend_pid( )
        AND
            -- Exclude known applications connections
            application_name !~ '(?:psql)|(?:pgAdmin.+)'
        AND
            -- Include connections to the same database the thread is connected to
            datname = current_database()
        AND
            -- Include connections using the same thread username connection
            usename = current_user
        AND
            -- Include inactive connections only
            state in ('idle', 'idle in transaction', 'idle in transaction (aborted)', 'disabled')
        AND
            -- Include old connections (found with the state_change field)
            current_timestamp - state_change > interval '5 minutes'
    )
    SELECT
        pg_terminate_backend(pid)
    FROM
        inactive_connections
    WHERE
        rank > 1 -- Leave one connection for each application connected to the database
    """)
    cur.close()
    conn.close()
    engine.dispose()

def enterElement(timeTemp,amountTemp):
    engine = sqlalchemy.create_engine(URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        newEntry = dashInfo(
            time=timeTemp,
            amount=amountTemp
        )
        session.add(newEntry)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        print("makes it into the finally *******")
        session.close_all()
        engine.dispose()
    # print(getMostRecentPull())

def getMostRecentPull():
    engine = sqlalchemy.create_engine(URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        lastElement = session.query(dashInfo).first()
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        sessions.close_all()
        engine.dispose()
    return str(lastElement)

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
    # marketMoverData_dict = {}

    engine = sqlalchemy.create_engine(URL)
    con = engine.connect()

    for marketSize in marketSize_list:
        for timeLength in timeLength_list:
            # marketMoverData_dict[(marketSize+"-"+timeLength)] = getMarketMoverData(marketSize,timeLength, tickers_df,ticker_df_dict).to_json()
            df = getMarketMoverData(marketSize,timeLength, tickers_df,ticker_df_dict).rename({'% Change': 'Percent Change'}, axis=1)
            df = df.nlargest(10,'Percent Change').append(df.nsmallest(10,'Percent Change'))
            table_name = marketSize+"-"+timeLength
            df.to_sql(table_name, con, if_exists='replace')

    con.close()
    engine.dispose()
    # with open('JSON Files/marketMoverData_dict.json', 'w') as fp:
    #     json.dump(new_marketMoverData_dict, fp)
    # print("Finished creating market mover data")
    # pickle.dump(marketMoverData_dict, open("pickleFiles/marketMoverData_dict.p", "wb" ), protocol=-1)

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


        # with open('JSON Files/tickers_df.json', 'w') as fp:
        #     json.dump(temp_tickers_df.to_json(), fp)

        # pickle.dump(temp_tickers_df, open("pickleFiles/tickers_df.p", "wb" ), protocol=-1)

        today1 = datetime.datetime.now(EST).strftime("%Y-%m-%d %I:%M %p")
        enterElement(today1, len(temp_tickers_df.index))
        # with open("JSON Files/datetime.txt", "w+") as f:
        #     f.write(today1)

        # pickle.dump(today1, open('pickleFiles/datetime','wb') )
        # print("Completed JSON dumps")


    print("Completed yfinance data pull")

    ticker_df_dict = ticker_df_dict_temp
    getEverythingFromMarketMover(tickers_df,ticker_df_dict)



    # with open('JSON Files/tickers_df.json', 'w') as fp:
    #     json.dump(tickers_df.to_json(), fp)
    # pickle.dump(tickers_df, open("pickleFiles/tickers_df.p", "wb" ), protocol=-1)


    today1 = datetime.datetime.now(EST).strftime("%Y-%m-%d %I:%M %p")
    enterElement(today1, len(tickers_df.index))
    # with open("JSON Files/datetime.txt", "w+") as f:
    #     f.write(today1)
    # # pickle.dump(today1, open('pickleFiles/datetime','wb') )
    # print("Completed final Pickle dumps")
    # pickle.dump(ticker_df_dict, open("pickleFiles/ticker_df_dict.p", "wb" ), protocol=-1)
