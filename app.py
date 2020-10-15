import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import pandas_datareader as web
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = dash.Dash(__name__)

app.layout = html.Div(children=[

    html.Div(children='''
        symbol to plot:
    '''),

    dcc.Input(id='input', value='', type='text'),
    html.Button(id='submit-button', n_clicks=0, children='Find Ticker'),

    html.Div(id='output-graph')
])


@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='submit-button', component_property='n_clicks')],
    [State(component_id='input', component_property='value')]
)
def update_graph(n_clicks, input):
    tag = 'WIKI/{}'.format(input.upper())

    df = web.DataReader(tag, 'quandl', '01-01-2015',
                        '02-08-2018', api_key=os.getenv('QUANDL_API_KEY'))

    return dcc.Graph(
        id='output-graph',
        figure={
            'data': [
                {'x': df.index, 'y': df['Close'],
                    'type': 'line', 'name': 'input_data'}
            ],
            'layout': {
                'title': input
            }
        }
    )


if __name__ == "__main__":
    app.run_server(debug=True)
