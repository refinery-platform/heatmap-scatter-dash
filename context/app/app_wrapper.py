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
        self.app.css.append_css({
            'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'
        })
        self.app.scripts.append_script({
            'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js'
        })

        conditions_options = [
            {'label': cond, 'value': cond}
            for cond in self._conditions
        ]

        pc_options = [
            {'label': pc, 'value': pc}
            for pc in ['pc1', 'pc2', 'pc3', 'pc4']  # TODO: DRY
        ]

        def dropdown(id, options, axis, axis_index):
            return html.Span(
                [
                    html.Label(
                        [axis],
                        className='col-sm-1 control-label'
                    ),
                    dcc.Dropdown(
                        id='scatter-{}-{}-axis-select'.format(id, axis),
                        options=options,
                        value=options[axis_index]['value'],
                        className='col-sm-5'
                    )
                ]
            )

        def scatter(id, options, search=False, log=False):
            control_nodes = [
                html.Div([
                    dropdown(id, options, 'x', 0),
                    dropdown(id, options, 'y', 1)
                ],
                className='form-group')
            ]
            if search:
                control_nodes.insert(0, html.Div([
                    html.Label(
                        ['gene'],
                        className='col-sm-1 control-label'
                    ),
                    html.Div([
                        dcc.Input(
                            id='search-{}'.format(id),
                            placeholder='search...',
                            type="text",
                            className='form-control')
                    ],
                    className='col-sm-11')
                ],
                className='form-group'))
            nodes = [
                dcc.Graph(
                    id='scatter-{}'.format(id),
                    style={'height': '33vh'}
                ),
                html.Div(control_nodes, className='form-horizontal')
            ]
            return html.Div(nodes, className='tab-pane active', id=id)

        self.app.layout = html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='heatmap',
                        style={'height': '100vh'}
                    ),
                ],
                className='col-md-6'),
                html.Div([
                    html.Ul([
                        html.Li([
                            html.A([
                                'PCA'
                            ],
                                href='#pca',
                                className='active'
                            )
                        ])
                    ],
                    className='nav nav-tabs'),
                    html.Div([
                        scatter('pca', pc_options),
                    ]),
                    html.Ul([
                        html.Li([
                            html.A([
                                'Genes'
                            ],
                            href='#genes',
                            className='active'
                            )
                        ]),
                        html.Li([
                            html.A([
                                'Volcano'
                            ],
                            href='#volcano')
                        ])
                    ],
                    className='nav nav-tabs'),
                    html.Div([
                        scatter('genes', conditions_options, search=True),
                        scatter('volcano', conditions_options)
                    ],
                    className='tab-content')

                ],
                className='col-md-6')
            ],
            className='row')
        ],
        className='container')

    def _configure_callbacks(self):
        genes = self._dataframe.axes[0].tolist()

        def figure_output(id):
            return Output(component_id=id, component_property='figure')

        def gene_match_booleans(search_term):
            return [search_term in gene for gene in genes]

        @self.app.callback(
            figure_output('heatmap'),
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
                        z=self._dataframe[booleans].as_matrix(),
                        colorscale=[
                            # Plotly offers only linear color scales,
                            # but you can set up your own color scale,
                            # setting different colors at exponential points.
                            # https://plot.ly/python/logarithmic-color-scale/
                            [0, 'rgb(0, 0, 100)'],
                            [0.001, 'rgb(25, 0, 75)'],
                            [0.01, 'rgb(50, 0, 50)'],
                            [0.1, 'rgb(75, 0, 25)'],
                            [1, 'rgb(100, 0, 0)']
                        ]
                    )
                ],
                'layout': go.Layout(
                    xaxis={
                        'ticks': '',
                        'tickangle': 90},
                    yaxis={
                        'ticks': '',
                        'showticklabels': False},
                    margin={'l': 75, 'b': 100, 't': 30, 'r': 0}
                    # Need top margin so infobox on hover is not truncated
                )
            }

        def scatter_layout(x_axis, y_axis, x_log=False, y_log=False):
            x_axis_config = {'title': x_axis}
            y_axis_config = {'title': y_axis}
            if x_log:
                x_axis_config['type'] = 'log'
            if y_log:
                y_axis_config['type'] = 'log'
            return go.Layout(
                xaxis=x_axis_config,
                yaxis=y_axis_config,
                margin=go.Margin(
                    l=80,
                    r=20,
                    b=60,
                    t=20,
                    pad=5
                )
            )

        def scatter_inputs(id, search=False):
            inputs = [
                Input(
                    component_id='scatter-{}-{}-axis-select'.format(id, axis),
                    component_property='value') for axis in ['x', 'y']
            ]
            if search:
                inputs.append(
                    Input(component_id='search-{}'.format(id),
                          component_property='value')
                )
            return inputs

        @self.app.callback(
            figure_output('scatter-pca'),
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
            figure_output('scatter-genes'),
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
                'layout': scatter_layout(
                    x_axis, y_axis,
                    x_log=True, y_log=True)
            }

        @self.app.callback(
            figure_output('scatter-volcano'),
            scatter_inputs('volcano')
        )
        def update_scatter_volcano(x_axis, y_axis):
            return {
                'data': [
                    go.Scattergl(
                        x=self._dataframe[x_axis],
                        y=self._dataframe[y_axis],
                        mode='markers'
                    )
                ],
                'layout': scatter_layout(x_axis, y_axis)
            }
