import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from dash import Dash
import pandas

app = Dash()
app.layout = html.Div([
    'Type something here and it will redraw:',
    dcc.Input(id='my_input'),
    dcc.Graph(id='my_graph')
])

@app.callback(
    Output('my_graph', 'figure'),
    [Input('my_input', 'value')]
)
def not_a_reproducer_sadly(input):
    good = pandas.DataFrame(
        [[1, 2],
         [3, 4]],
        columns=['x', 'y']
    )
    empty = pandas.DataFrame(
        columns=['x', 'y']
    )

    data = [ go.Scattergl(x=good['x'], y=good['y'], text=good.index) ]
    if input:
        data.append(go.Scattergl(x=empty['x'], y=empty['y'], text=None))

    return {
        'data': data,
        'layout': go.Layout()
    }

app.run_server()