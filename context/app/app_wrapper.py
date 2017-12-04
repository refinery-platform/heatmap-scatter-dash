import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from app.cluster import cluster
from app.pca import pca


class AppWrapper:

    def __init__(self, dataframe, clustering=False):
        self._dataframe = cluster(dataframe) if clustering else dataframe
        self._dataframe_pca = pca(dataframe)
        self._conditions = self._dataframe.axes[1].tolist()
        self.app = dash.Dash()
        self._configure_layout()
        self._configure_callbacks()

    def _configure_layout(self):
        half_width = {'width': '50%', 'display': 'inline-block'}

        conditions_options = [
            {'label': cond, 'value': cond}
            for cond in self._conditions
        ]

        self.app.layout = html.Div([
            html.Div([
                # First row
                dcc.Graph(
                    id='heatmap',
                    style=half_width
                ),
                dcc.Graph(
                    id='scatter-pca',
                    style=half_width
                ),
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
                                value=self._conditions[0]
                            )],
                            style=half_width
                        ),
                        html.Div(
                            [dcc.Dropdown(
                                id='scatter-y-axis-select',
                                options=conditions_options,
                                value=self._conditions[1]
                            )],
                            style=half_width
                        )
                    ],
                    style=half_width),
                'TODO: Volcano'
            ])
        ])

    def _configure_callbacks(self):
        genes = self._dataframe.axes[0].tolist()

        def gene_match_booleans(search_term):
            return [search_term in gene for gene in genes]

        @self.app.callback(
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
                        x=self._conditions,
                        y=matching_genes,
                        z=self._dataframe[booleans].as_matrix()
                    )
                ],
                'layout': go.Layout(
                    xaxis={
                        'ticks': '',
                        'showticklabels': True,
                        'tickangle': 90},
                    yaxis={
                        'ticks': '',
                        'showticklabels': False},
                    margin={'l': 75, 'b': 100, 't': 30, 'r': 0}
                    # Need top margin so infobox on hover is not truncated
                )
            }

        @self.app.callback(
            Output(component_id='scatter-pca', component_property='figure'),
            [
                # TODO
            ]
        )
        def update_scatter_pca():
            return {
                'data': [
                    go.Scattergl(
                        x=self._dataframe_pca['pc1'],
                        y=self._dataframe_pca['pc2'],
                        mode='markers'
                    )
                ],
                'layout': go.Layout(
                    # xaxis={
                    #     'ticks': '',
                    #     'showticklabels': Tr},
                    # yaxis={
                    #     'ticks': '',
                    #     'showticklabels': False},
                    margin={'l': 75, 'b': 100, 't': 30, 'r': 0}
                    # Need top margin so infobox on hover is not truncated
                )
            }

        @self.app.callback(
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
                        x=self._dataframe[x_axis][booleans],
                        y=self._dataframe[y_axis][booleans],
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
