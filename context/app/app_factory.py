import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from app.cluster import cluster


def make_app(dataframe, clustering=False):
    app = dash.Dash()

    if clustering:
        dataframe = cluster(dataframe)

    conditions = dataframe.axes[1].tolist()
    genes = dataframe.axes[0].tolist()

    half_width = {'width': '50%', 'display': 'inline-block'}

    conditions_options = [
        {'label': cond, 'value': cond}
        for cond in conditions
    ]

    app.layout = html.Div([
        html.Div([
            # First row
            dcc.Graph(
                id='heatmap',
                style=half_width
            ),
            'TODO: PCA'
        ]),
        html.Div([
            # Second row
            html.Div(
                [
                    dcc.Graph(
                        id='scatter'
                    ),
                    html.Div([
                        dcc.Input(
                            id='search',
                            placeholder='Search genes...',
                            type="text")
                    ]),
                    html.Div(
                        [dcc.Dropdown(
                            id='scatter-x-axis-select',
                            options=conditions_options,
                            value=conditions[0]
                        )],
                        style=half_width
                    ),
                    html.Div(
                        [dcc.Dropdown(
                            id='scatter-y-axis-select',
                            options=conditions_options,
                            value=conditions[1]
                        )],
                        style=half_width
                    )
                ],
                style=half_width),
            'TODO: Volcano'
        ])
    ])

    def gene_match_booleans(search_term):
        return [search_term in gene for gene in genes]

    @app.callback(
        Output(component_id='scatter', component_property='figure'),
        [
            Input(component_id='search',
                  component_property='value'),
            Input(component_id='scatter-x-axis-select',
                  component_property='value'),
            Input(component_id='scatter-y-axis-select',
                  component_property='value')
        ]
    )
    def update_scatter(search_term, x_axis, y_axis):
        if not search_term:
            search_term = ''
        booleans = gene_match_booleans(search_term)
        return {
            'data': [
                go.Scattergl(
                    # TODO: try go.pointcloud if we need something faster?
                    x=dataframe[x_axis][booleans],
                    y=dataframe[y_axis][booleans],
                    mode='markers'
                )
            ],
            'layout': go.Layout(
                xaxis={'title': x_axis},
                yaxis={'title': y_axis},
                margin={'l': 75, 'b': 50, 't': 0, 'r': 0}
                # Axis labels lie in the margin.
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
                go.Heatmapgl(
                    x=conditions,
                    y=matching_genes,
                    z=dataframe[booleans].as_matrix()
                )
            ],
            'layout': go.Layout(
                xaxis={'ticks': '', 'showticklabels': True, 'tickangle': 90},
                yaxis={'ticks': '', 'showticklabels': False},
                margin={'l': 75, 'b': 100, 't': 0, 'r': 0}
            )
        }

    return app
