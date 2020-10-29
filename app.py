# from apscheduler.schedulers.background import BackgroundScheduler
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
# import timeit
# from contextlib import contextmanager
# import sys, os
# from tqdm import tqdm
# import pickle
# import pytz
# import json
from worker import getMostRecentPull, createTickerDict
import sqlalchemy
# import clock.py
# from clock import startScheduler

createTickerDict("compilation_testSize.csv")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title='Stock Dashboard'
marketSize_list = ['Total Market', 'Only ETFs', 'Only Fortune 500']
timeLength_list = ['1 Day', '1 Week', '1 Month', '1 Year']
tickers_df = pd.read_csv('Tickers/compilation.csv')
# URL = "postgresql://postgres:Maroon6248@localhost/dashboard-database"
URL = 'postgres://rrfjatgyxoplxp:85abb6064386584979cf0d6ddb56ed5e3154d743afd18dd42e4e6c46287f9f40@ec2-18-210-90-1.compute-1.amazonaws.com:5432/d9qtfjohvv68rv'

#app layout
def make_layout():
    # update = getMostRecentPull
    return html.Div(children=[
    html.Img(src=app.get_asset_url('my-logo.jpeg'), style={'width':'100px', 'position':'absolute','top':'50px','left':'5%', 'borderRadius':'20px'}),

    html.H1(id='firstElement', children='Stock Dashboard', style={'fontSize':'60px','marginTop':'50px','marginBottom':0,'marginLeft':'110px', 'color':'rgb(0,83,148)','fontWeight':'700'}),

    html.Div(children='''
        Built with Dash: A web application framework for Python.
    ''', style={'float':'clear','marginLeft':'110px'}),
    html.H3("Pricing Graph and Market Mover Table",  style={'marginTop':'30px','marginBottom':'0px', 'color':'rgb(103,144,153)'}),

    # html.H6("Currently have "+str(len(pickle.load( open("pickleFiles/tickers_df.p", "rb") ).index)) +" out of 9211 stocks loaded. Last pull: "+str(pickle.load(open('pickleFiles/datetime','rb')))+" EST", style={'marginTop':'0px', 'marginBottom':'20px', 'color':'rgb(103,144,153)'}),
    html.H6(id="introElement", style={'marginTop':'0px', 'marginBottom':'20px', 'color':'rgb(103,144,153)'}),

    html.Div([
        html.Div([
            "Search any stock or ETF on NASDAQ, AMEX, or NYSE: ",
            dcc.Dropdown(
                id='ticker-name',
                # options=[{'label': str(row['Symbol']) +" - "+str(row['Name']), 'value': row['Symbol']} for index, row in tickers_df.iterrows()],
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
            columns=[{"name": i, "id": i} for i in ['Symbol', 'Percent Change', 'Price', 'Volume']],
            style_header={
                'fontWeight': 'bold',
                'fontSize': '18px',
                'width': '25%',
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
            columns=[{"name": i, "id": i} for i in ['Symbol', 'Percent Change', 'Price', 'Volume']],
            # columns=[{"name": i, "id": i} for i in market_df.columns],
            # data=market_df.nsmallest(10,'% Change').to_dict('records'),
            style_header={
                'fontWeight': 'bold',
                'fontSize': '18px',
                'width': '25%',
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

@app.callback(
    Output('introElement', 'children'),
    [Input('firstElement', 'children')])
def set_cities_options(value):
    engine = sqlalchemy.create_engine(URL)
    con = engine.connect()
    var = "Total Market-1 Day"
    dataFrame = pd.read_sql("select * from \""+var+"\"", con);
    con.close()
    engine.dispose()
    return "Currently have {} out of 9211 stocks loaded. Last pull: {} EST".format(dataFrame['amount'][0], dataFrame['timeIndex'][0])

@app.callback(
    Output('ticker-name', 'options'),
    [Input('firstElement', 'children')])
def set_cities_options(value):
    return [{'label': str(row['Symbol']) +" - "+str(row['Name']), 'value': row['Symbol']} for index, row in tickers_df.iterrows()]

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
def table1(value, period):

    engine = sqlalchemy.create_engine(URL)
    con = engine.connect()
    var = value+"-"+period
    dataFrame = pd.read_sql("select * from \""+var+"\"", con);
    con.close()
    engine.dispose()
    dataFrame = dataFrame.drop(['timeIndex','amount'], axis=1)
    dataFrame = dataFrame.nsmallest(10,'Percent Change')
    dataFrame['Percent Change'] = dataFrame['Percent Change'].apply(lambda x: round(x, 2))
    return dataFrame.to_dict('records')

#callback for market loser table
@app.callback(
    Output('marketmover_table2', 'data'),
    [Input('marketLoser-cat1', 'value'),
     Input('marketLoser-cat2', 'value'),
      ])
def table2(value, period):

    engine = sqlalchemy.create_engine(URL)
    con = engine.connect()
    var = value+"-"+period
    dataFrame = pd.read_sql("select * from \""+var+"\"", con);
    con.close()
    engine.dispose()
    dataFrame = dataFrame.drop(['timeIndex','amount'], axis=1)
    dataFrame = dataFrame.nsmallest(10,'Percent Change')
    dataFrame['Percent Change'] = dataFrame['Percent Change'].apply(lambda x: round(x, 2))
    return dataFrame.to_dict('records')

app.layout = make_layout

if __name__ == '__main__':
    app.run_server(use_reloader=False, debug=True)
    # app.run_server(debug=True)
    # app.run_server(use_reloader=False)
