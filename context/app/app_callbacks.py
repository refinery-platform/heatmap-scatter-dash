from math import log10

import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly.figure_factory.utils import label_rgb, n_colors, unlabel_rgb

from app.app_layout import AppLayout


class AppCallbacks(AppLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        callback = self.app.callback

        callback(
            _figure_output('heatmap'),
            [
                Input('search-genes', 'value'),
                Input('scale-select', 'value'),
                Input('scatter-pca', 'selectedData'),
                Input('scatter-genes', 'selectedData')
            ]
        )(self._update_heatmap)

        callback(
            _figure_output('scatter-pca'),
            _scatter_inputs('pca')
        )(self._update_scatter_pca)

        callback(
            _figure_output('scatter-genes'),
            _scatter_inputs('genes', search=True, scale_select=True)
        )(self._update_scatter_genes)

        callback(
            _figure_output('scatter-volcano'),
            _scatter_inputs('volcano') +
            [Input('file-select', 'value')]
        )(self._update_scatter_volcano)

        callback(
            Output('table-iframe', 'srcDoc'),
            [Input('search-genes', 'value')]
        )(self._update_table)

    def _update_heatmap(
            self,
            gene_search_term,
            scale,
            pca_selected,
            genes_selected):
        if pca_selected:
            selected_conditions = _select(
                pca_selected['points'], self._conditions)
        else:
            selected_conditions = self._conditions
        selected_conditions_df = self._dataframe[selected_conditions]

        if genes_selected:
            selected_genes = _select(
                genes_selected['points'], self._genes, gene_search_term)
            selected_conditions_genes_df = \
                selected_conditions_df.loc[selected_genes]
        else:
            selected_conditions_genes_df = \
                selected_conditions_df[
                    _match_booleans(gene_search_term, self._genes)
                ]

        show_genes = len(selected_conditions_genes_df.index.tolist()) < 40
        return {
            'data': [
                self._heatmap(selected_conditions_genes_df, scale == 'log')
            ],
            'layout': go.Layout(
                xaxis={'ticks': '', 'tickangle': 90},
                yaxis={'ticks': '', 'showticklabels': show_genes},
                margin={'l': 75, 'b': 75, 't': 30, 'r': 0}
                # Need top margin so infobox on hover is not truncated
            )
        }

    def _heatmap(self, dataframe, is_log_scale):
        adjusted_color_scale = (
            _linear(self._color_scale) if not is_log_scale
            else _log_interpolate(
                self._color_scale,
                min([x for x in
                     dataframe.values.flatten()
                     if x > 0]),  # We will take the log, so exclude zeros.
                dataframe.max().max()))

        if self._heatmap_type == 'svg':
            constructor = go.Heatmap
        elif self._heatmap_type == 'canvas':
            constructor = go.Heatmapgl
        else:
            raise Exception('Unknown heatmap type: ' + self._heatmap_type)
        return constructor(
            x=dataframe.columns.tolist(),
            y=dataframe.index.tolist(),
            z=dataframe.as_matrix(),
            colorscale=adjusted_color_scale)

    def _update_scatter_pca(self, x_axis, y_axis, heatmap_range):
        return {
            'data': [
                go.Scattergl(
                    x=self._dataframe_pca[x_axis],
                    y=self._dataframe_pca[y_axis],
                    mode='markers',
                    text=self._dataframe_pca.index
                )
            ],
            'layout': _ScatterLayout(x_axis, y_axis)
        }

    def _update_scatter_genes(
            self,
            x_axis, y_axis,
            heatmap_range, search_term, scale):
        if not search_term:
            search_term = ''
        booleans = _match_booleans(search_term, self._genes)
        is_log = scale == 'log'
        return {
            'data': [
                go.Scattergl(
                    # TODO: try go.pointcloud if we need something faster?
                    x=self._dataframe[x_axis][booleans],
                    y=self._dataframe[y_axis][booleans],
                    mode='markers',
                    text=self._dataframe.index
                )
            ],
            'layout': _ScatterLayout(
                x_axis, y_axis,
                x_log=is_log, y_log=is_log)
        }

    def _update_scatter_volcano(self, x_axis, y_axis, heatmap_range, file):
        if not x_axis:
            # ie, there are no differential files.
            # "file" itself is (mis)used for messaging.
            return {}
        return {
            'data': [
                go.Scattergl(
                    x=self._diff_dataframes[file][x_axis],
                    y=self._diff_dataframes[file][y_axis],
                    mode='markers',
                    text=self._dataframe.index
                )
            ],
            'layout': _ScatterLayout(x_axis, y_axis)
        }

    def _update_table(self, search_term):
        booleans = _match_booleans(search_term, self._genes)
        return ''.join(
            [
                '<link rel="stylesheet" property="stylesheet" href="{}">'
                .format(url) for url in self._css_urls
            ] + [self._dataframe[booleans].to_html()]
        )


def _select(points, target, search_term=None):
    point_numbers = [
        point['pointNumber'] for point in points
        if not search_term or search_term in point['text']
    ]
    # TODO: Why not just return point['text'] here?
    return [
        item for (i, item)
        in enumerate(target)
        if i in point_numbers
    ]


def _log_interpolate(color_scale, min, max):
    if len(color_scale) > 2:
        raise Exception('Expected just two points on color scale')
    log10(min)
    points = int(log10(max) - log10(min)) + 2
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


def _figure_output(id):
    return Output(id, 'figure')


def _match_booleans(search_term, targets):
    # search_term may be None on first load.
    return [(search_term or '') in s for s in targets]


class _ScatterLayout(go.Layout):
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


def _scatter_inputs(id, search=False, scale_select=False):
    inputs = [
        Input('scatter-{}-{}-axis-select'.format(id, axis), 'value')
        for axis in ['x', 'y']
    ]
    inputs.append(
        Input(
            'heatmap', 'relayoutData'
        )
    )
    if search:
        inputs.append(
            Input('search-{}'.format(id), 'value')
        )
    if scale_select:
        inputs.append(
            Input('scale-select', 'value')
        )
    return inputs
