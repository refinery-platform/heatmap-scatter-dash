import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas
from io import StringIO

app = dash.Dash()

csv = StringIO("""gene,cond1,cond2,cond3,cond4
gene-one,0.2,0.7,0.2,0.7
gene-two,0.4,0.8,0.2,0.8
gene-three,0.5,0.8,0.1,0.9
gene-four,0.6,0.8,0.3,0.8
gene-five,0.6,0.9,0.4,0.8
gene-six,0.6,0.9,0.5,0.8
""")
df = pandas.read_csv(csv, index_col=0)
conditions = df.axes[1].tolist()
genes = df.axes[0].tolist()

style = {'width': '50%', 'display': 'inline-block'}

app.layout = html.Div([
    html.Div([
        dcc.Input(id='search', placeholder='Search genes...', type="text"),
    ]),
    dcc.Graph(
        id='scatter',
        style=style
    ),
    dcc.Graph(
        id='heatmap',
        figure={
            'data': [
                go.Heatmap(
                    x=conditions,
                    y=genes,
                    z=df.as_matrix()
                )
            ]
        },
        style=style
    )
])

@app.callback(
    Output(component_id='scatter', component_property='figure'),
    [Input(component_id='search', component_property='value')]
)
def update_scatter(search_term):
    matching = [search_term in gene if search_term else True for gene in genes]
    return {
        'data': [
            go.Scatter(
                x=df['cond1'][matching],
                y=df['cond2'][matching],
                mode='markers'
            )
        ]
    }

if __name__ == '__main__':
    app.run_server(debug=True)