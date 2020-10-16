import sqlite3
import pandas as pd
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
import plotly.express as px
from collections import deque
from datetime import datetime
import dash_bootstrap_components as dbc
import logging

logging.basicConfig(filename='dash_app.log', level=logging.DEBUG, format='%(levelname)-%(asctime)s-%(message)s')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div(children=[
    html.Div(children=[
        html.Div(children=[
            dbc.Alert(
                'No results for the search term',
                id='no-results-alert',
                color='danger',
                is_open=False
            ),

            html.H2('Live Twitter Sentiment'),

            html.Div(children=[
                html.Small('enter a search term below...')
            ])
        ], className='mt-3'),

        dcc.Input(
            id='search-term',
            value='',
            type='text',
            className='form-control'
        ),

        dcc.Graph(
            id='live-graph',
            animate=False
        ),

        dcc.Interval(
            id='graph-update',
            interval=1000
        )
    ], className='container')

])


@app.callback(
    [Output(component_id='live-graph', component_property='figure'),
     Output(component_id='no-results-alert', component_property='is_open')],
    [Input(component_id='graph-update', component_property='n_intervals'),
     Input(component_id='search-term', component_property='value')]
)
def update_graph(n, search_term):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()

        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 1000", conn, params=('%' + search_term + '%',))
        df.sort_values('unix', inplace=True)

        if df.size == 0:
            return {}, True
            logging.warning('No values for search term {}'.format(search_term))

        df['sentiment_ra'] = df['sentiment'].rolling(window=int(len(df) / 5)).mean()
        df['timestamp'] = pd.to_datetime(df['unix'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('US/Mountain')
        df.set_index('timestamp', inplace=True)

        if df.size > 1000:
            df = df.resample('1s').mean()


        df.dropna(inplace=True)

        X = df.index[-100:]
        Y = df['sentiment_ra'].values[-100:]

        data = go.Scatter(
            x=list(X),
            y=list(Y),
            name='Scatter',
            mode='lines+markers'
        )

        return {
            'data': [data],
            'layout': go.Layout(
                xaxis=dict(range=[min(X), max(X)]),
                yaxis=dict(range=[min(Y) - 0.1, max(Y) + 0.1])
            )
        }, False
    
    except Exception as e:
        logging.error(str(e))


if __name__ == "__main__":
    app.run_server(debug=True)
