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

    def figure_output(id):
        return Output(component_id=id, component_property='figure')

    def match_booleans(search_term, targets):
        return [search_term in s for s in targets]

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
    def update_heatmap(gene_search_term, scale, pca_selected, genes_selected):

        # pca: TODO: Fix the copy and paste between these two.

        if pca_selected:
            pca_points = [
                point['pointNumber'] for point in pca_selected['points']
            ]
            selected_conditions = [
                condition for (i, condition)
                in enumerate(app_wrapper._conditions)
                if i in pca_points
            ]
        else:
            selected_conditions = app_wrapper._conditions
        selected_conditions_df = app_wrapper._dataframe[selected_conditions]

        # genes:

        gene_search_term = gene_search_term or ''
        if genes_selected:
            gene_points = [
                point['pointNumber'] for point in genes_selected['points']
                if gene_search_term in point['text']
            ]
            selected_genes = [
                gene for (i, gene) in enumerate(app_wrapper._genes)
                if i in gene_points
            ]
            selected_conditions_genes_df = \
                selected_conditions_df.loc[selected_genes]
        else:
            selected_conditions_genes_df = \
                selected_conditions_df[
                    match_booleans(gene_search_term, app_wrapper._genes)
                ]
        # TODO: Text search is being done two different ways. Unify.

        # style:

        adjusted_color_scale = (
            _linear(app_wrapper._color_scale) if scale != 'log'
            else _log_interpolate(app_wrapper._color_scale))

        heatmap_type = app_wrapper._heatmap_type
        if heatmap_type == 'svg':
            heatmap_constructor = go.Heatmap
        elif heatmap_type == 'canvas':
            heatmap_constructor = go.Heatmapgl
        else:
            raise Exception('Unknown heatmap type: ' + heatmap_type)

        show_genes = len(selected_conditions_genes_df.index.tolist()) < 40
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
                    'showticklabels': show_genes},
                margin={'l': 75, 'b': 75, 't': 30, 'r': 0}
                # Need top margin so infobox on hover is not truncated
            )
        }

    class ScatterLayout(go.Layout):
        def __init__(self, x_axis, y_axis, x_log=False, y_log=False):
            x_axis_config = {'title': x_axis}
            y_axis_config = {'title': y_axis}
            if x_log:
                x_axis_config['type'] = 'log'
            if y_log:
                y_axis_config['type'] = 'log'
            super().__init__(
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
                    mode='markers',
                    text=app_wrapper._dataframe_pca.index
                )
            ],
            'layout': ScatterLayout(x_axis, y_axis)
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
        booleans = match_booleans(search_term, app_wrapper._genes)
        is_log = scale == 'log'
        return {
            'data': [
                go.Scattergl(
                    # TODO: try go.pointcloud if we need something faster?
                    x=app_wrapper._dataframe[x_axis][booleans],
                    y=app_wrapper._dataframe[y_axis][booleans],
                    mode='markers',
                    text=app_wrapper._dataframe.index
                )
            ],
            'layout': ScatterLayout(
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
                    mode='markers',
                    text=app_wrapper._dataframe.index
                )
            ],
            'layout': ScatterLayout(x_axis, y_axis)
        }

    @callback(
        Output(component_id='table-iframe', component_property='srcDoc'),
        [
            Input(component_id='search-genes',
                  component_property='value')
        ]
    )
    def update_table(search_term):
        booleans = match_booleans(search_term, app_wrapper._genes)
        return ''.join(
            [
                '<link rel="stylesheet" property="stylesheet" href="{}">'
                .format(url) for url in app_wrapper.css_urls
            ] + [app_wrapper._dataframe[booleans].to_html()]
        )
