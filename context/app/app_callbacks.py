import plotly.graph_objs as go
from dash.dependencies import Input, Output


def configure_callbacks(app_wrapper):
    callback = app_wrapper.app.callback
    genes = app_wrapper._dataframe.axes[0].tolist()

    def figure_output(id):
        return Output(component_id=id, component_property='figure')

    def gene_match_booleans(search_term):
        return [search_term in gene for gene in genes]

    @callback(
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
                    x=app_wrapper._conditions,
                    y=matching_genes,
                    z=app_wrapper._dataframe[booleans].as_matrix(),
                    colorscale=app_wrapper._color_scale)
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
                l=80,  # noqa: E741
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

    @callback(
        figure_output('scatter-pca'),
        scatter_inputs('pca')
    )
    def update_scatter_pca(x_axis, y_axis):
        return {
            'data': [
                go.Scattergl(
                    x=app_wrapper._dataframe_pca[x_axis],
                    y=app_wrapper._dataframe_pca[y_axis],
                    mode='markers'
                )
            ],
            'layout': scatter_layout(x_axis, y_axis)
        }

    @callback(
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
                    x=app_wrapper._dataframe[x_axis][booleans],
                    y=app_wrapper._dataframe[y_axis][booleans],
                    mode='markers'
                )
            ],
            'layout': scatter_layout(
                x_axis, y_axis,
                x_log=True, y_log=True)
        }

    @callback(
        figure_output('scatter-volcano'),
        scatter_inputs('volcano')
    )
    def update_scatter_volcano(x_axis, y_axis):
        return {
            'data': [
                go.Scattergl(
                    x=app_wrapper._dataframe[x_axis],
                    y=app_wrapper._dataframe[y_axis],
                    mode='markers'
                )
            ],
            'layout': scatter_layout(x_axis, y_axis)
        }
