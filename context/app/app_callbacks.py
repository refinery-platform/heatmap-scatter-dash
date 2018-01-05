import json
import re
import time
from math import log10

import pandas
import plotly.graph_objs as go
from dash.dependencies import Input
from plotly.figure_factory.utils import label_rgb, n_colors, unlabel_rgb

from app.app_condition_callbacks import AppConditionCallbacks
from app.app_gene_callbacks import AppGeneCallbacks
from app.utils.callbacks import figure_output


class AppCallbacks(AppGeneCallbacks, AppConditionCallbacks):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app.callback(
            figure_output('heatmap'),
            [
                Input('selected-genes-ids-json', 'children'),
                Input('scale-select', 'value')
            ]
        )(self._update_heatmap)

    def _search_to_ids_json(self, input):
        self.info('_search_to_ids_json', input)
        ids = [
            i for (i, gene)
            in enumerate(self._genes)
            if ((input or '') in gene)
        ]
        return json.dumps(ids)

    def _scatter_to_ids_json(self, input):
        self.info('_scatter_to_ids_json', input)
        ids = list(set([
            x['pointNumber'] for x in input['points']
        ])) if input else []
        return json.dumps(ids)

    def _update_timestamp(self, input):
        self.info('_update_timestamp', input)
        return time.time()

    def _pick_latest(self, *timestamps_and_states):
        self.info('_pick_latest', timestamps_and_states)
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
        # TODO: Re-enable PCA
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


def _match_booleans(search_term, index_set, targets):
    # search_term may be None on first load.
    # index set should be ignored if empty
    return [
        (search_term or '') in s
        and (i in index_set or not index_set)
        for (i, s) in enumerate(targets)
    ]
