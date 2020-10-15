import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque

X = deque(maxlen=20)
Y = deque(maxlen=20)
X.append(1)
Y.append(1)

app = dash.Dash(__name__)
app.layout = html.Div(children=[

    dcc.Graph(
        id='live-graph',
        animate=True
    ),

    dcc.Interval(
        id='graph-update',
        interval=1000
    )

])


@app.callback(
    Output(component_id='live-graph', component_property='figure'),
    [Input(component_id='graph-update', component_property='n_intervals')]
)
def update_graph(n):
    global X, Y
    X.append(X[-1] + 1)
    Y.append(Y[-1] + Y[-1] * random.uniform(-0.1, 0.1))

    data = go.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines+markers'
    )

    return {
        'data': [data],
        'layout': go.Layout(
            xaxis=dict(range=[min(X) - 0.1, max(X) + 0.1]),
            yaxis=dict(range=[min(Y) - 0.1, max(Y) + 0.1])
        )
    }


if __name__ == "__main__":
    app.run_server(debug=True)
