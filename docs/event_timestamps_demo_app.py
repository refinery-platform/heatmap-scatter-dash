import time
import json
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from dash import Dash

def update_timestamp(input):
    return time.time()

def choose_latest(*timestamps_and_states):
    assert len(timestamps_and_states) % 2 == 0
    midpoint = len(timestamps_and_states) // 2
    timestamps = timestamps_and_states[:midpoint]
    states = timestamps_and_states[midpoint:]
    most_recent = states[timestamps.index(max(timestamps))]
    return json.dumps(most_recent)

app = Dash()

app.layout = html.Div([
    dcc.Input(id='input-a', type="text"),
    dcc.Input(id='input-b', type="text"),
    dcc.Input(id='input-c', type="text"),
    html.Div(
        [
            'Timestamps:', html.Br(),
            'A: ', html.Span(id='input-a-timestamp'), html.Br(),
            'B: ', html.Span(id='input-b-timestamp'), html.Br(),
            'C: ', html.Span(id='input-c-timestamp'), html.Br(),
        ],
        style={'display': 'block'}  # Switch this on or off for debugging.
    ),
    html.Span(['and the latest value is: ']),
    html.Span(id='latest-value')
])

app.callback(
    Output('input-a-timestamp', 'children'), [Input('input-a', 'value')]
)(update_timestamp)
app.callback(
    Output('input-b-timestamp', 'children'), [Input('input-b', 'value')]
)(update_timestamp)
app.callback(
    Output('input-c-timestamp', 'children'), [Input('input-c', 'value')]
)(update_timestamp)

app.callback(
    Output('latest-value', 'children'),
    [Input('input-a-timestamp', 'children'),
     Input('input-b-timestamp', 'children'),
     Input('input-c-timestamp', 'children')],
    [State('input-a', 'value'),
     State('input-b', 'value'),
     State('input-c', 'value')]
)(choose_latest)

app.run_server()