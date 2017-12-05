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

        pc_options = [
            {'label': pc, 'value': pc}
            for pc in ['pc1', 'pc2', 'pc3', 'pc4']  # TODO: DRY
        ]

        def scatter(id, options, search=False):
            nodes = [
                dcc.Graph(
                    id='scatter-{}'.format(id)
                ),
                html.Div(
                    [dcc.Dropdown(
                        id='scatter-{}-x-axis-select'.format(id),
                        options=options,
                        value=options[0]['value']
                    )],
                    style=half_width
                ),
                html.Div(
                    [dcc.Dropdown(
                        id='scatter-{}-y-axis-select'.format(id),
                        options=options,
                        value=options[1]['value']
                    )],
                    style=half_width
                )
            ]
            if search:
                nodes.insert(1, html.Div([
                            dcc.Input(
                                id='search-{}'.format(id),
                                placeholder='Search...',
                                type="text")
                ]))
            return html.Div(nodes, style=half_width)

        self.app.layout = html.Div([
            html.Div([
                # First row
                dcc.Graph(
                    id='heatmap',
                    style=half_width
                ),
                scatter('pca', pc_options)
            ]),
            html.Div([
                # Second row
                scatter('genes', conditions_options, search=True),
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
                Input(component_id='search-genes', component_property='value')
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

        def scatter_layout(x_axis, y_axis):
            return go.Layout(
                xaxis={'title': x_axis},
                yaxis={'title': y_axis},
                margin={'l': 75, 'b': 50, 't': 0, 'r': 0}
            )

        def scatter_inputs(id, search=False):
            inputs = [
                Input(component_id='scatter-{}-x-axis-select'.format(id),
                      component_property='value'),
                Input(component_id='scatter-{}-y-axis-select'.format(id),
                      component_property='value')
            ]
            if search:
                inputs.append(
                    Input(component_id='search-{}'.format(id),
                          component_property='value')
                )
            return inputs

        @self.app.callback(
            Output(component_id='scatter-pca', component_property='figure'),
            scatter_inputs('pca')
        )
        def update_scatter_pca(x_axis, y_axis):
            return {
                'data': [
                    go.Scattergl(
                        x=self._dataframe_pca[x_axis],
                        y=self._dataframe_pca[y_axis],
                        mode='markers'
                    )
                ],
                'layout': scatter_layout(x_axis, y_axis)
            }

        @self.app.callback(
            Output(component_id='scatter-genes', component_property='figure'),
            scatter_inputs('genes', search=True)
        )
        def update_scatter_genes(x_axis, y_axis, search_term):
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
                'layout': scatter_layout(x_axis, y_axis)
            }
