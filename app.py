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

conditions_options = [{'label': cond, 'value': cond} for cond in conditions]

app.layout = html.Div([
    html.Div([
        dcc.Input(id='search', placeholder='Search genes...', type="text"),
        dcc.Dropdown(
            id='scatter-x-axis-select',
            options=conditions_options,
            value=conditions[0]
        ),
        dcc.Dropdown(
            id='scatter-y-axis-select',
            options=conditions_options,
            value=conditions[1]
        )
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
    [
        Input(component_id='search', component_property='value'),
        Input(component_id='scatter-x-axis-select', component_property='value'),
        Input(component_id='scatter-y-axis-select', component_property='value')
    ]
)
def update_scatter(search_term, x_axis, y_axis):
    if not search_term:
        search_term = ''
    booleans = gene_match_booleans(search_term)
    return {
        'data': [
            go.Scatter(
                x=df[x_axis][booleans],
                y=df[y_axis][booleans],
                mode='markers'
            )
        ],
        'layout': go.Layout(
            xaxis={'range': [0, 1], 'title': x_axis},
            yaxis={'range': [0, 1], 'title': y_axis}
        )
    }

@app.callback(
    Output(component_id='heatmap', component_property='figure'),
    [
        Input(component_id='search', component_property='value')
    ]
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