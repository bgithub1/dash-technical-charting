# In[]:
# Import required libraries
import os
import datetime as dt

import quantmod as qm
import pandas_datareader.data as web
import pandas as pd
import flask
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from flask_caching import Cache


# In[]:
# Setup the app_deprecated
server = flask.Flask(__name__)
app = dash.Dash(__name__)

app.scripts.config.serve_locally = False
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

url_constituents = 'https://datahub.io/core/s-and-p-500-companies/r/constituents.csv'
df_constit = pd.read_csv(url_constituents)

# In[]:
# Put your Dash code here

# Add caching
cache = Cache(app.server, config={'CACHE_TYPE': 'simple'})
timeout = 60 * 60  # 1 hour

# Controls
spydr_sector_names = ['SPY','XLE','XLU','XLK','XLB','XLP','XLY','XLI','XLC','XLV','XLF']
spydr_short_names = list(df_constit.Symbol)

sp500 = spydr_short_names

tickers = sp500 + spydr_sector_names
tickers = [dict(label=str(ticker), value=str(ticker))
           for ticker in tickers]

# Dynamic binding
functions = list(filter(lambda s: 'add_' in s.lower(),dir(qm.ta)))
functions = [dict(label=str(function[4:]), value=str(function))
             for function in functions]

# Layout
app.layout = html.Div(
    [
        html.Div([
            html.H2(
                'Dash Finance',
                style={'padding-top': '20', 'text-align': 'center'}
            ),
            html.Div(
                [
                    html.Label('Select ticker:'),
                    dcc.Dropdown(
                        id='dropdown',
                        options=tickers,
                        value='SPY',
                    ),
                ],
                style={
                    'width': '510', 'display': 'inline-block',
                    'padding-left': '40', 'margin-bottom': '20'}
            ),
            html.Div(
                [
                    html.Label('Select technical indicators:'),
                    dcc.Dropdown(
                        id='multi',
                        options=functions,
                        multi=True,
#                         value=['add_BBANDS', 'add_RSI', 'add_MACD'],
                        value=['add_MA'],
                    ),
                ],
                style={
                    'width': '510', 'display': 'inline-block',
                    'padding-right': '40', 'margin-bottom': '20'}
            ),
        ]),
        html.Div(
            [
                html.Label('Specify parameters of technical indicators:'),
                html.P('Use , to separate arguments and ; to separate indicators. () and spaces are ignored'),  # noqa: E501
                dcc.Input(
                    id='arglist',
                    style={'height': '32', 'width': '1020'}
                )
            ],
            id='arg-controls',
            style={'display': 'none'}
        ),
        dcc.Graph(id='output')
    ],
    style={
        'width': '1100',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'font-family': 'overpass',
        'background-color': '#F3F3F3'
    }
)

@app.callback(Output('arg-controls', 'style'), [Input('multi', 'value')])
def display_control(multi):
    if not multi:
        return {'display': 'none'}
    else:
        return {'margin-bottom': '20', 'padding-left': '40'}


@cache.memoize(timeout=timeout)
@app.callback(Output('output', 'figure'), [Input('dropdown', 'value'),
                                           Input('multi', 'value'),
                                           Input('arglist', 'value')])
def update_graph_from_dropdown(dropdown, multi, arglist):
 
    # Get Quantmod Chart
    df = web.DataReader(dropdown, 'yahoo', dt.datetime(2016, 1, 1), dt.datetime.now())
    print('Loading')
    ch = qm.Chart(df)
 
    # Get functions and arglist for technical indicators
    if arglist:
        arglist = arglist.replace('(', '').replace(')', '').split(';')
        arglist = [args.strip() for args in arglist]
        for function, args in zip(multi, arglist):
            if args:
                args = args.split(',')
                newargs = []
                for arg in args:
                    try:
                        arg = int(arg)
                    except:
                        try:
                            arg = float(arg)
                        except:
                            pass
                    newargs.append(arg)
                print(newargs)
                # Dynamic calling
                getattr(qm, function)(ch, *newargs)
            else:
                getattr(qm, function)(ch)
    else:
        for function in multi:
            # Dynamic calling
            getattr(qm, function)(ch)
 
    # Return plot as figure
    fig = ch.to_figure(width=1100)
    return fig




external_css = ["https://fonts.googleapis.com/css?family=Overpass:400,400i,700,700i",
                "https://cdn.rawgit.com/plotly/dash-app_deprecated-stylesheets/c6a126a684eaaa94a708d41d6ceb32b28ac78583/dash-technical-charting.css"]

for css in external_css:
    app.css.append_css({"external_url": css})

if 'DYNO' in os.environ:
    app.scripts.append_script({
        'external_url': 'https://cdn.rawgit.com/chriddyp/ca0d8f02a1659981a0ea7f013a378bbd/raw/e79f3f789517deec58f41251f7dbb6bee72c44ab/plotly_ga.js'
    })


# In[]:
# Run the Dash app_deprecated
if __name__ == '__main__':
    app.server.run(port=8500)
