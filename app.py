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
        style=style
    )
])

def gene_match_booleans(search_term):
    return [search_term in gene for gene in genes]

@app.callback(
    Output(component_id='scatter', component_property='figure'),
    [Input(component_id='search', component_property='value')]
)
def update_scatter(search_term):
    if not search_term:
        search_term = ''
    booleans = gene_match_booleans(search_term)
    return {
        'data': [
            go.Scatter(
                x=df['cond1'][booleans],
                y=df['cond2'][booleans],
                mode='markers'
                # xmin=0,
                # xmax=1,
                # ymin=0,
                # ymax=1
            )
        ],
        'layout': go.Layout(
            xaxis=dict(
                range=[0,1]
            ),
            yaxis=dict(
                range=[0, 1]
            )
        )
    }

@app.callback(
    Output(component_id='heatmap', component_property='figure'),
    [Input(component_id='search', component_property='value')]
)
def update_heatmap(search_term):
    if not search_term:
        search_term = ''
    booleans = gene_match_booleans(search_term)
    matching_genes = [gene for gene in genes if search_term in gene]
    return {
        'data': [
            go.Heatmap(
                x=conditions,
                y=matching_genes,
                z=df[booleans].as_matrix(),
                zmax=1,
                zmin=0
            )
        ]
    }

if __name__ == '__main__':
    app.run_server(debug=True)