'''
Created on Feb 4, 2019

@author: bperlman1
'''
import dash
import quantmod as qm
import datetime as dt
import pandas_datareader.data as web
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)
df = web.DataReader('SPY', 'yahoo', dt.datetime(2016, 1, 1), dt.datetime.now())
print('Loading')
ch = qm.Chart(df)
fig = ch.to_figure(width=1100)

app.layout = html.Div(
    [
        dcc.Graph(id='my-graph',figure=fig),
    ], 
)

if __name__=='__main__':
    app.server.run(port=8500)
    
    
    
    