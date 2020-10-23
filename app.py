from apscheduler.schedulers.background import BackgroundScheduler

from datetime import date
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf


tabtitle='Stock Dashboard'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title=tabtitle

#pull all ticker information
# tickers_df = pd.concat(map(pd.read_csv, ['Tickers/nasdaq.csv', 'Tickers/amex.csv','Tickers/nyse.csv']))
tickers_df = pd.read_csv('Tickers/compilation.csv')
tickers_df = pd.read_csv('Tickers/compilation_testSize.csv')

#initialize table_df
# table_df = yf.download(tickers=tickers_df['Symbol'].to_list(), period='1y', group_by='ticker', threads=False)

#Amount of seconds between update
# UPDADE_INTERVAL = 120

print("here in the code")
# table_df = yf.download(tickers=tickers_df['Symbol'].to_list(), period='1y', group_by='ticker', threads=False)

scheduler = BackgroundScheduler(daemon=True)

# def updateTableDF():
#     print('Updating table_df.')
#     scheduler.print_jobs()
#     table_df = yf.download(tickers=tickers_df['Symbol'].to_list(), period='1y', group_by='ticker', threads=False)

scheduler.add_job(lambda : scheduler.print_jobs(),'cron',day_of_week='mon-fri', hour=18, minute=40, timezeon='EST')
# scheduler.add_job(updateTableDF,'cron',hour=2, timezone='EST')
# scheduler.start()

def getMarketMoverData(category, timeLength):
    print("*******")
    print(category)
    print("*******")
    return pd.read_csv('Tickers/market_df.csv')
    table_list = []

    for index, row in tickers_df.iterrows():

        if category=="Only ETFs" and row['ETF'] == 'Y':
            column = row['Symbol']
            if timeLength == "1 Day":
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-1]-1)*100
            elif timeLength == "1 Week":
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-7]-1)*100
            elif timeLength == "1 Month":
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-30]-1)*100
            else:
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[1]-1)*100
            if pd.isna(percentChange) == False:
                percentChange = round(percentChange, 2)
                volume = "{:,}".format(int(table_df[column]['Volume'].iloc[-1]))
                tempList = [column, percentChange, round(table_df[column]['Adj Close'].iloc[-1],2), volume]
                table_list.append(tempList)
        elif category == "Only Fortune 500" and row['Fortune 500'] == 'Y':
            column = row['Symbol']
            if timeLength == "1 Day":
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-1]-1)*100
            elif timeLength == "1 Week":
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-7]-1)*100
            elif timeLength == "1 Month":
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-30]-1)*100
            else:
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[1]-1)*100
            if pd.isna(percentChange) == False:
                percentChange = round(percentChange, 2)
                volume = "{:,}".format(int(table_df[column]['Volume'].iloc[-1]))
                tempList = [column, percentChange, round(table_df[column]['Adj Close'].iloc[-1],2), volume]
                table_list.append(tempList)
        elif category=="Total Market":
            column = row['Symbol']
            if timeLength == "1 Day":
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-1]-1)*100
            elif timeLength == "1 Week":
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-7]-1)*100
            elif timeLength == "1 Month":
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[-30]-1)*100
            else:
                percentChange = (table_df[column]['Adj Close'].iloc[-1]/table_df[column]['Open'].iloc[1]-1)*100
            if pd.isna(percentChange) == False:
                percentChange = round(percentChange, 2)
                volume = "{:,}".format(int(table_df[column]['Volume'].iloc[-1]))
                tempList = [column, percentChange, round(table_df[column]['Adj Close'].iloc[-1],2), volume]
                table_list.append(tempList)

    return pd.DataFrame(table_list, columns=['Symbol', '% Change', 'Price', 'Volume'])

#app layout
def make_layout():
    return html.Div(children=[
    html.H1(children='Stock Dashboard'),

    html.Div(children='''
        Built with Dash: A web application framework for Python.
    '''),
    html.H2("Pricing Graph"),
    html.Div([
        html.Div([
            "Search any stock or ETF on NASDAQ, AMEX, or NYSE: ",
            dcc.Dropdown(
                id='ticker-name',
                options=[{'label': str(row['Name'])+" ("+str(row['Symbol'])+")", 'value': row['Symbol']} for index, row in tickers_df.iterrows()],
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
            style={'width': '74%', 'float': 'right', "display":"inline-block", 'borderLeft':'4px solid #828282'}
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
                options=[{'label': i, 'value': i} for i in ['Total Market','Only ETFs','Only Fortune 500']],
                value='Total Market',
                # optionHeight=50
            )
        ], style={'display':'inline-block', 'width':'49%'}),
        html.Div([
            "Time period: ",
            dcc.Dropdown(
                id='marketGainer-cat2',
                options=[{'label': i, 'value': i} for i in ['1 Day', '1 Week', '1 Month', '1 Year']],
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
            # shapes = [dict(
            #     x0='2016-12-09', x1='2016-12-09', y0=0, y1=1, xref='x', yref='paper',
            #     line_width=2)],
            # annotations=[dict(
            #     x='2016-12-09', y=0.05, xref='x', yref='paper',
            #     showarrow=False, xanchor='left', text='Increase Period Begins')]
            # margin={'t': 40},
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
     Input('marketGainer-cat2', 'value')])
def update_stock_graph(value, period):
    temp_df = getMarketMoverData(value,period)
    return temp_df.nlargest(10,'% Change').to_dict('records')

#callback for market loser table
@app.callback(
    Output('marketmover_table2', 'data'),
    [Input('marketLoser-cat1', 'value'),
     Input('marketLoser-cat2', 'value')])
def update_stock_graph2(value, period):
    temp_df = getMarketMoverData(value,period)
    return temp_df.nsmallest(10,'% Change').to_dict('records')
# get initial data
# get_new_data()

app.layout = make_layout

# sched.start()
# executor = ThreadPoolExecutor(max_workers=1)
# executor.submit(get_new_data_every)

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server()
