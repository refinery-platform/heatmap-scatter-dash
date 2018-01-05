import re
from math import log10

import json
import time
import pandas
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from plotly.figure_factory.utils import label_rgb, n_colors, unlabel_rgb

from app.app_layout import AppLayout


class AppCallbacks(AppLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app.callback(
            _figure_output('heatmap'),
            [
                Input('selected-genes-ids-json', 'children'),
                Input('scale-select', 'value')
            ]
        )(self._update_heatmap)

        # self.app.callback(
        #     _figure_output('scatter-pca'),
        #     _scatter_inputs('pca')
        # )(self._update_scatter_pca)

        self.app.callback(
            _figure_output('scatter-sample-by-sample'),
            [Input('selected-genes-ids-json', 'children')] +
            _scatter_inputs('sample-by-sample', scale_select=True)
        )(self._update_scatter_genes)

        self.app.callback(
            _figure_output('scatter-volcano'),
            [Input('selected-genes-ids-json', 'children'),
             Input('file-select', 'value')] +
            _scatter_inputs('volcano', scale_select=False)
        )(self._update_scatter_volcano)

        # self.app.callback(
        #     Output('ids-iframe', 'srcDoc'),
        #     [Input('scatter-pca', 'selectedData')]
        # )(self._update_condition_list)

        self.app.callback(
            Output('table-iframe', 'srcDoc'),
            [Input('selected-genes-ids-json', 'children')]
        )(self._update_gene_table)

        self.app.callback(
            Output('list-iframe', 'srcDoc'),
            [Input('selected-genes-ids-json', 'children')]
        )(self._update_gene_list)

        # Hidden elements that record the last time a control was touched:

        self.app.callback(
            Output('search-genes-timestamp', 'children'),
            [Input('search-genes', 'value')]
        )(self._update_timestamp)

        self.app.callback(
            Output('scatter-sample-by-sample-timestamp', 'children'),
            [Input('scatter-sample-by-sample', 'selectedData')]
        )(self._update_timestamp)

        self.app.callback(
            Output('scatter-volcano-timestamp', 'children'),
            [Input('scatter-volcano', 'selectedData')]
        )(self._update_timestamp)

        # Hidden elements which transform inputs into lists of IDs:

        self.app.callback(
            Output('search-genes-ids-json', 'children'),
            [Input('search-genes', 'value')]
        )(self._search_to_ids_json)

        self.app.callback(
            Output('scatter-sample-by-sample-ids-json', 'children'),
            [Input('scatter-sample-by-sample', 'selectedData')]
        )(self._scatter_to_ids_json)

        self.app.callback(
            Output('scatter-volcano-ids-json', 'children'),
            [Input('scatter-volcano', 'selectedData')]
        )(self._scatter_to_ids_json)

        # Hidden elements which pick the value from the last modified control:

        self.app.callback(
            Output('selected-genes-ids-json', 'children'),
            [Input('search-genes-timestamp', 'children'),
             Input('scatter-sample-by-sample-timestamp', 'children'),
             Input('scatter-volcano-timestamp', 'children')],
            [State('search-genes-ids-json', 'children'),
             State('scatter-sample-by-sample-ids-json', 'children'),
             State('scatter-volcano-ids-json', 'children')]
        )(self._pick_latest)

    def _search_to_ids_json(self, input):
        ids = [
            i for (i,gene)
            in enumerate(self._genes)
            if ((input or '') in gene)
        ]
        return json.dumps(ids)

    def _scatter_to_ids_json(self, input):
        ids = list(set([
            x['pointNumber'] for x in input['points']
        ])) if input else []
        return json.dumps(ids)

    def _update_timestamp(self, input):
        return time.time()

    def _pick_latest(self, *timestamps_and_states):
        assert len(timestamps_and_states) % 2 == 0
        midpoint = len(timestamps_and_states) // 2
        timestamps = timestamps_and_states[:midpoint]
        states = timestamps_and_states[midpoint:]
        latest = states[timestamps.index(max(timestamps))]
        return latest

    def _update_heatmap(
            self,
            selected_genes_ids_json,
            scale):
    #     if pca_selected:
    #         selected_conditions = _select(
    #             pca_selected['points'], self._conditions)
    #     else:
        selected_conditions = self._conditions
        selected_conditions_df = self._dataframe[selected_conditions]

        selected_conditions_genes_df = self._filter_by_genes_ids_json(
            selected_conditions_df,
            selected_genes_ids_json
        )

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

    # def _update_scatter_pca(self, x_axis, y_axis, heatmap_range):
    #     return {
    #         'data': [
    #             go.Scattergl(
    #                 x=self._dataframe_pca[x_axis],
    #                 y=self._dataframe_pca[y_axis],
    #                 mode='markers',
    #                 text=self._dataframe_pca.index,
    #                 marker=_dark_dot
    #             )
    #         ],
    #         'layout': _ScatterLayout(x_axis, y_axis)
    #     }

    def _update_scatter_genes(
            self,
            selected_genes_ids_json,
            x_axis, y_axis, scale):
        is_log = scale == 'log'
        all = self._dataframe
        selected = self._filter_by_genes_ids_json(
            all,
            selected_genes_ids_json
        )
        return {
            'data': [
                go.Scattergl(
                    x=all[x_axis],
                    y=all[y_axis],
                    mode='markers',
                    text=all.index,
                    marker=_light_dot,
                ),
                go.Scattergl(
                    x=selected[x_axis],
                    y=selected[y_axis],
                    mode='markers',
                    text=selected.index,
                    marker=_dark_dot
                )
            ],
            'layout': _ScatterLayout(
                x_axis, y_axis,
                x_log=is_log, y_log=is_log)
        }

    def _update_scatter_volcano(
            self,
            selected_genes_ids_json,
            file_selected,
            x_axis, y_axis):
        if not x_axis:
            # ie, there are no differential files.
            # "file" itself is (mis)used for messaging.
            return {}
        all = self._diff_dataframes[file_selected]
        selected = self._filter_by_genes_ids_json(
            all,
            selected_genes_ids_json
        )
        return {
            'data': [
                go.Scattergl(
                    x=all[x_axis],
                    y=all[y_axis],
                    mode='markers',
                    text=self._dataframe.index,
                    marker=_light_dot
                ),
                go.Scattergl(
                    x=selected[x_axis],
                    y=selected[y_axis],
                    mode='markers',
                    text=self._dataframe.index,
                    marker=_dark_dot
                )
            ],
            'layout': _ScatterLayout(x_axis, y_axis)
        }
    #
    # def _update_condition_list(self, selected_data):
    #     points = [point['pointNumber'] for point in selected_data['points']]
    #     return self._list_html(self._dataframe.T.iloc[points])
    #     # Alternatively:
    #     #   pandas.DataFrame(self._dataframe.columns.tolist())
    #     # but transpose may be more efficient than creating a new DataFrame.

    def _update_gene_table(self, selected_genes_ids_json):
        selected_genes_df = self._filter_by_genes_ids_json(
            self._dataframe,
            selected_genes_ids_json
        )
        return self._table_html(selected_genes_df)

    def _update_gene_list(self, selected_genes_ids_json):
        selected_genes_df = self._filter_by_genes_ids_json(
            self._dataframe,
            selected_genes_ids_json
        )
        return self._list_html(selected_genes_df)

    def _filter_by_genes_ids_json(self, dataframe, json_list):
        selected_genes_ids = json.loads(json_list)
        selected_genes = [
            item for (i, item)
            in enumerate(self._genes)
            if i in selected_genes_ids
        ]
        return dataframe.loc[selected_genes]

    def _table_html(self, dataframe):
        """
        Given a dataframe,
        returns the dataframe as an html table.
        """
        return self._css_url_html() + _remove_rowname_header(
            dataframe.to_html()
        )

    def _list_html(self, dataframe):
        """
        Given a dataframe,
        returns the indexes of the dataframe as a single column html table.
        """
        return self._css_url_html() + _remove_rowname_header(
            pandas.DataFrame(dataframe.index).to_html(
                index=False
            )
        )
        # Would prefer something like:
        #   dataframe.to_html(max_cols=0)
        # but that shows all columns, not just the row header.

    def _css_url_html(self):
        return ''.join([
            '<link rel="stylesheet" property="stylesheet" href="{}">'
            .format(url) for url in self._css_urls
        ])


_dark_dot = {
    'color': 'rgb(0,0,255)',
    'size': 5
}
_light_dot = {
    'color': 'rgb(127,127,255)',
    'size': 5
}


def _remove_rowname_header(s):
    return re.sub(r'<tr[^>]*>[^<]*<th>(rowname|0)</th>.*?</tr>', '', s,
                  count=1, flags=re.DOTALL)


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


def _match_booleans(search_term, index_set, targets):
    # search_term may be None on first load.
    # index set should be ignored if empty
    return [
        (search_term or '') in s
        and (i in index_set or not index_set)
        for (i, s) in enumerate(targets)
    ]


class _ScatterLayout(go.Layout):
    def __init__(self, x_axis, y_axis, x_log=False, y_log=False):
        x_axis_config = {'title': x_axis}
        y_axis_config = {'title': y_axis}
        if x_log:
            x_axis_config['type'] = 'log'
        if y_log:
            y_axis_config['type'] = 'log'
        super().__init__(
            showlegend=False,
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


def _scatter_inputs(id, scale_select=False):
    inputs = [
        Input('scatter-{}-{}-axis-select'.format(id, axis), 'value')
        for axis in ['x', 'y']
    ]
    if scale_select:
        inputs.append(
            Input('scale-select', 'value')
        )
    return inputs
