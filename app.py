from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
import timeit
from contextlib import contextmanager
import sys, os
from tqdm import tqdm
import pickle
import pytz
# from clock import startScheduler

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


app.title='Stock Dashboard'
marketSize_list = ['Total Market', 'Only ETFs', 'Only Fortune 500']
timeLength_list = ['1 Day', '1 Week', '1 Month', '1 Year']
EST = pytz.timezone('America/New_York')

# To supress print lines from yfinance
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
        today1 = datetime.datetime.now(EST).strftime("%Y-%m-%d %I:%M %p")
        pickle.dump(today1, open('pickleFiles/datetime','wb') )
        print("Completed Pickle dumps")
        # pickle.dump(ticker_df_dict_temp, open("pickleFiles/ticker_df_dict.p", "wb" ), protocol=-1)

    print("Completed yfinance data pull")

    ticker_df_dict = ticker_df_dict_temp
    getEverythingFromMarketMover(tickers_df,ticker_df_dict)
    pickle.dump(tickers_df, open("pickleFiles/tickers_df.p", "wb" ), protocol=-1)
    today1 = datetime.datetime.now(EST).strftime("%Y-%m-%d %I:%M %p")
    pickle.dump(today1, open('pickleFiles/datetime','wb') )
    print("Completed final Pickle dumps")
    # pickle.dump(ticker_df_dict, open("pickleFiles/ticker_df_dict.p", "wb" ), protocol=-1)

# createTickerDict('compilation_testSize.csv')
# createTickerDict('compilation.csv')

# scheduler = BackgroundScheduler(daemon=True)
# # scheduler = BlockingScheduler()
# @scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=10, minute=0, timezone='UTC')
# def scheduled_job():
#     print("**********")
#     print("inside cron job")
#     print("**********")
#     createTickerDict('compilation.csv')
# # startScheduler()
# scheduler.start()

#app layout
def make_layout():
    return html.Div(children=[

    # dcc.Store(id='memory', data=pickle.load( open("pickleFiles/ticker_df_dict full.p", "rb"))  ),
    # dcc.Store(id='memory', data=[pickle.load( open("pickleFiles/tickers_df full.p", "rb") ), pickle.load( open( "pickleFiles/ticker_df_dict full.p", "rb" ) )]  ),
    # html.Div(id='intermediate-value1', style={'display': 'none'}, children = [pickle.load( open("pickleFiles/tickers_df.p", "rb") ), pickle.load( open( "ticker_df_dict.p", "rb" ) )]   ),
    # html.Div(id='intermediate-value2', style={'display': 'none'}, children = pickle.load( open( "pickleFiles/ticker_df_dict.p", "rb" ) )),

    html.Img(src=app.get_asset_url('my-logo.jpeg'), style={'width':'100px', 'position':'absolute','top':'50px','left':'5%', 'borderRadius':'20px'}),

    html.H1(children='Stock Dashboard', style={'fontSize':'60px','marginTop':'50px','marginBottom':0,'marginLeft':'110px', 'color':'rgb(0,83,148)','fontWeight':'700'}),

    html.Div(children='''
        Built with Dash: A web application framework for Python.
    ''', style={'float':'clear','marginLeft':'110px'}),
    html.H3("Pricing Graph and Market Mover Table",  style={'marginTop':'30px','marginBottom':'0px', 'color':'rgb(103,144,153)'}),
    html.H6("Currently have "+str(len(pickle.load( open("pickleFiles/tickers_df.p", "rb") ).index)) +" out of 9211 stocks loaded. Last pull: "+str(pickle.load(open('pickleFiles/datetime','rb'))+" EST"), style={'marginTop':'0px', 'marginBottom':'20px', 'color':'rgb(103,144,153)'}),
    html.Div([
        html.Div([
            "Search any stock or ETF on NASDAQ, AMEX, or NYSE: ",
            dcc.Dropdown(
                id='ticker-name',
                options=[{'label': str(row['Symbol']) +" - "+str(row['Name']), 'value': row['Symbol']} for index, row in (pickle.load( open("pickleFiles/tickers_df.p", "rb"))).iterrows()],
                value='SPY',
                placeholder='stock/ETF (such as SPY)',
                # optionHeight=50
            ),
            html.Br(),
            "Date Range",
            dcc.RadioItems(
                id='ticker-date-range-options',
                options=[{'label': i, 'value': i} for i in ['Preset', 'Custom Range']],
                value='Preset',
                labelStyle={'display': 'inline-block'}
            ),
            html.Br(),
            dcc.RadioItems(
                id='ticker-preset',
                options=[{'label': i[0], 'value': i[1]} for i in [['1 Day','1d'],['5 Days','5d'],['1 Month','1mo'],['6 Months','6mo'], ['1 Year','1y'], ['5 Years','5y'], ['All Time','max']]],
                value='1d'
            ),
            dcc.DatePickerRange(
                id='ticker-custom-range',
                # min_date_allowed=date(1995, 8, 5),
                max_date_allowed=date.today(),
                initial_visible_month=date(2019, 8, 5),
                start_date=date(2019, 8, 5),
                end_date=date.today()
            ),
            html.Br(),
            "Graph Type:",
            dcc.RadioItems(
                id='graph-type',
                options=[{'label': i, 'value': i} for i in ['Candlestick', 'Line Graph']],
                value='Candlestick',
                labelStyle={'display': 'inline-block'}
            ),
            # dcc.Input(id='ticker-custom-range', placeholder='initial value', type='text'),
            html.Br(),
            html.Div(id='graph-output-state')
            ],
            style={"width": "24%", "display":"inline-block", 'height':'450px'}
        ),
        dcc.Graph(
            id='stock-graph',
            style={'width': '74%', 'float': 'right', "display":"inline-block", 'borderLeft':'1px solid #828282'}
        ),
    ], style={'border': '4px solid #828282', 'borderRadius': '10px', 'padding': '15px'}),
    html.Div([
        # html.H2('Market Movers')
    ], style={'paddingTop':40,'clear':'both'}),
    html.Div([
        html.H6(["Biggest Market Gainers"],style={'fontWeight':'bold','textAlign':"center"}),
        html.Div([
            "Sort by: ",
            dcc.Dropdown(
                id='marketGainer-cat1',
                options=[{'label': i, 'value': i} for i in marketSize_list],
                value='Total Market',
                # optionHeight=50
            )
        ], style={'display':'inline-block', 'width':'49%'}),
        html.Div([
            "Time period: ",
            dcc.Dropdown(
                id='marketGainer-cat2',
                options=[{'label': i, 'value': i} for i in timeLength_list],
                value='1 Day',
                # optionHeight=50
            )
        ], style={'display':'inline-block', 'width':'49%', 'float':'right'}),
        html.Br(),
        html.Br(),
        dash_table.DataTable(
            id='marketmover_table1',
            columns=[{"name": i, "id": i} for i in ['Symbol', '% Change', 'Price', 'Volume']],
            style_header={
                'fontWeight': 'bold',
                'fontSize': '18px',
                'font-family': "Open Sans, HelveticaNeue, Helvetica Neue"
            },
            style_cell={
                'textAlign': 'center',
                'height': '50px',
                'font-family': "Open Sans, HelveticaNeue, Helvetica Neue"
            },
            # style_table={'width': '40%', 'display': 'inline-block'}
        ),
    ], style={'width': '45%', 'display': 'inline-block', 'float': 'left', 'border': '4px solid #828282', 'borderRadius': '10px', 'padding': '15px'}),
    html.Div([
        html.H6(["Biggest Market Losers"],style={'fontWeight':'bold', 'textAlign':"center"}),
        html.Div([
            "Sort by: ",
            dcc.Dropdown(
                id='marketLoser-cat1',
                options=[{'label': i, 'value': i} for i in ['Total Market','Only ETFs','Only Fortune 500']],
                value='Total Market',
                # optionHeight=50
            )
        ], style={'display':'inline-block', 'width':'49%'}),
        html.Div([
            "Time period: ",
            dcc.Dropdown(
                id='marketLoser-cat2',
                options=[{'label': i, 'value': i} for i in ['1 Day', '1 Week', '1 Month', '1 Year']],
                value='1 Day',
                # optionHeight=50
            )
        ], style={'display':'inline-block', 'width':'49%', 'float':'right'}),
        html.Br(),
        html.Br(),
        dash_table.DataTable(
            id='marketmover_table2',
            columns=[{"name": i, "id": i} for i in ['Symbol', '% Change', 'Price', 'Volume']],
            # columns=[{"name": i, "id": i} for i in market_df.columns],
            # data=market_df.nsmallest(10,'% Change').to_dict('records'),
            style_header={
                'fontWeight': 'bold',
                'fontSize': '18px',
                'font-family': "Open Sans, HelveticaNeue, Helvetica Neue"
            },
            style_cell={
                'textAlign': 'center',
                'height': '50px',
                'font-family': "Open Sans, HelveticaNeue, Helvetica Neue"
            },

        )
    ], style={'width': '45%', 'display': 'inline-block', 'float':'right', 'border': '4px solid #828282', 'borderRadius': '10px', 'padding': '15px'}),
    html.Div([], style={'padding':60,'clear':'both'})
], style={'marginLeft': '5%', 'marginRight': '5%'})

#callback to hide and unhide picking the date range for the stock graph
@app.callback([
   Output(component_id='ticker-preset', component_property='style'),
   Output(component_id='ticker-custom-range', component_property='style')],
   [Input(component_id='ticker-date-range-options', component_property='value')])
def show_hide_element(value):
    if value == 'Preset':
        return {'display': 'block'}, {'display': 'none'}
    if value == 'Custom Range':
        return {'display': 'none'}, {'display': 'block'}

#callback for creating the graph
@app.callback(
    Output('stock-graph', 'figure'),
    [Input('ticker-name', 'value'),
     Input('ticker-date-range-options', 'value'),
     Input('ticker-preset', 'value'),
     Input('ticker-custom-range', 'start_date'),
     Input('ticker-custom-range', 'end_date'),
     Input('graph-type', 'value')])
def update_stock_graph(ticker, option, dateSet, dateCustomStart, dateCustomEnd, graphType):
    if option == 'Preset':
        interval = '1d'
        if dateSet == "1d":
            interval = '5m'
        if graphType == 'Candlestick':
            if dateSet == '6mo':
                interval = '1d'
            elif dateSet == '1y':
                interval = '5d'
            elif dateSet == '5y':
                interval = '1mo'
            elif dateSet == 'max':
                interval = '1wk'
        yfinanceInfo = yf.download(ticker, period=dateSet, interval=interval, threads=False)
    else:
        yfinanceInfo = yf.download(ticker, start=dateCustomStart, end=dateCustomEnd, threads=False)
    percentChange = (yfinanceInfo['Adj Close'].iloc[-1] / yfinanceInfo['Adj Close'].iloc[0])-1
    percentChange = round(percentChange*100, 2)
    title = '<b>Stock Pricing for {}.</b><br>Percent change in stock price: {}%<br>'.format(ticker, percentChange)
    # title = "Stock Pricing for "+str(ticker)+". Percent change in stock price: "+str(percentChange)+"%"

    if graphType == "Candlestick":
        fig = go.Figure(data=[go.Candlestick(x=yfinanceInfo.index,
                    open=yfinanceInfo['Open'],
                    high=yfinanceInfo['High'],
                    low=yfinanceInfo['Low'],
                    close=yfinanceInfo['Adj Close'])])
        fig.update_layout(
            title=title,
            yaxis_title=str(ticker)+' Price in $',
            xaxis_title='Time Period: '+dateSet,
            template='plotly_white',
            hovermode='x unified'
        )
    else:
        fig = px.line(yfinanceInfo, y="Adj Close", title=title, template='plotly_white')
        fig.update_traces(hovertemplate='Date: %{x} <br>Price: $%{y}')
        fig.update_layout(
            # margin={'t': 40},
            hovermode='x unified'
        )
        fig.update_xaxes(title='Time Period: '+dateSet)
        fig.update_yaxes(title=str(ticker)+' Price in $')
    return fig

#callback for market gainer table
@app.callback(
    Output('marketmover_table1', 'data'),
    [Input('marketGainer-cat1', 'value'),
     Input('marketGainer-cat2', 'value'),
     ])
def update_stock_graph(value, period):
    marketMoverData_dict = pickle.load( open("pickleFiles/marketMoverData_dict.p", "rb") )
    temp_df = marketMoverData_dict[(value,period)]
    # temp_df = getMarketMoverData(value,period, data[0],data[1])
    return temp_df.nlargest(10,'% Change').to_dict('records')

#callback for market loser table
@app.callback(
    Output('marketmover_table2', 'data'),
    [Input('marketLoser-cat1', 'value'),
     Input('marketLoser-cat2', 'value'),
      ])
def update_stock_graph2(value, period):
    marketMoverData_dict = pickle.load( open("pickleFiles/marketMoverData_dict.p", "rb") )
    temp_df = marketMoverData_dict[(value,period)]
    # temp_df = getMarketMoverData(value,period, data[0],data[1])
    return temp_df.nsmallest(10,'% Change').to_dict('records')

app.layout = make_layout

if __name__ == '__main__':
    # app.run_server(use_reloader=False, debug=True)
    # app.run_server(debug=True)
    app.run_server(use_reloader=False)
