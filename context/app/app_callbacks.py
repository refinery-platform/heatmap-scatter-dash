import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly.figure_factory.utils import label_rgb, n_colors, unlabel_rgb


def _log_interpolate(color_scale):
    if len(color_scale) > 2:
        raise Exception('Expected just two points on color scale')
    points = 5  # TODO: We actually need to log the smallest value.
    interpolated = n_colors(
        unlabel_rgb(color_scale[1]),
        unlabel_rgb(color_scale[0]),
        points)
    missing_zero = [
        [10 ** -i, label_rgb(interpolated[i])]
        for i in reversed(range(points))
    ]
    # Without a point at zero, Plotly gives a color scale
    # that is mostly greys. No idea why.
    return [[0, label_rgb(interpolated[points - 1])]] + missing_zero


def _linear(color_scale):
    return [[0, color_scale[0]], [1, color_scale[1]]]


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
            Input(component_id='search-genes',
                  component_property='value'),
            Input(component_id='scale-select',
                  component_property='value'),
            Input(component_id='scatter-pca',
                  component_property='selectedData'),
            Input(component_id='scatter-genes',
                  component_property='selectedData')
        ]
    )
    def update_heatmap(search_term, scale, pca_selected, genes_selected):
        pca_points = (
            [point['pointNumber'] for point in pca_selected['points']]
            if pca_selected else None)
        # gene_points = ([point['pointNumber']
        # for point in genes_selected['points']]
        #                if genes_selected else None)  # TODO

        selected_conditions = [
            condition for (i, condition) in enumerate(app_wrapper._conditions)
            if i in pca_points
        ] if pca_points else app_wrapper._conditions

        selected_conditions_df = app_wrapper._dataframe[selected_conditions]

        adjusted_color_scale = (
            _linear(app_wrapper._color_scale) if scale != 'log'
            else _log_interpolate(app_wrapper._color_scale))

        if not search_term:
            search_term = ''
        selected_conditions_genes_df = selected_conditions_df[
            gene_match_booleans(search_term)
        ]

        heatmap_type = app_wrapper._heatmap_type
        if heatmap_type == 'svg':
            heatmap_constructor = go.Heatmap
        elif heatmap_type == 'canvas':
            heatmap_constructor = go.Heatmapgl
        else:
            raise Exception('Unknown heatmap type: ' + heatmap_type)

        return {
            'data': [
                heatmap_constructor(
                    x=selected_conditions_genes_df.columns.tolist(),
                    y=selected_conditions_genes_df.index.tolist(),
                    z=selected_conditions_genes_df.as_matrix(),
                    colorscale=adjusted_color_scale)
            ],
            'layout': go.Layout(
                xaxis={
                    'ticks': '',
                    'tickangle': 90},
                yaxis={
                    'ticks': '',
                    'showticklabels': False},
                margin={'l': 75, 'b': 75, 't': 30, 'r': 0}
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

    def scatter_inputs(id, search=False, scale_select=False):
        inputs = [
            Input(
                component_id='scatter-{}-{}-axis-select'.format(id, axis),
                component_property='value') for axis in ['x', 'y']
        ]
        inputs.append(
            Input(
                component_id='heatmap',
                component_property='relayoutData'
            )
        )
        if search:
            inputs.append(
                Input(component_id='search-{}'.format(id),
                      component_property='value')
            )
        if scale_select:
            inputs.append(
                Input(component_id='scale-select',
                      component_property='value')
            )
        return inputs

    @callback(
        figure_output('scatter-pca'),
        scatter_inputs('pca')
    )
    def update_scatter_pca(x_axis, y_axis, heatmap_range):
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
        scatter_inputs('genes', search=True, scale_select=True)
    )
    def update_scatter_genes(
            x_axis, y_axis,
            heatmap_range, search_term, scale):
        if not search_term:
            search_term = ''
        booleans = gene_match_booleans(search_term)
        is_log = scale == 'log'
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
                x_log=is_log,
                y_log=is_log)
        }

    @callback(
        figure_output('scatter-volcano'),
        scatter_inputs('volcano')
    )
    def update_scatter_volcano(x_axis, y_axis, heatmap_range):
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
