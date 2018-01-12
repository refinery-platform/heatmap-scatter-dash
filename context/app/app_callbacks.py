import json
import re
import time
from math import log10

import pandas
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly.figure_factory.utils import label_rgb, n_colors, unlabel_rgb

from app.app_condition_callbacks import AppConditionCallbacks
from app.app_gene_callbacks import AppGeneCallbacks
from app.utils.callbacks import figure_output
from app.utils.cluster import cluster
from app.utils.frames import sort_by_variance


class AppCallbacks(AppGeneCallbacks, AppConditionCallbacks):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app.callback(
            figure_output('heatmap'),
            [
                Input('selected-conditions-ids-json', 'children'),
                Input('selected-genes-ids-json', 'children'),
                Input('scale-select', 'value')
            ]
        )(self._update_heatmap)

        # TODO: Generate the heatmap from the dataframe... and also update the scatterplots
        self.app.callback(
            Output('heatmap-dataframe-json', 'children'),
            [
                Input('selected-conditions-ids-json', 'children'),
                Input('selected-genes-ids-json', 'children'),
                Input('scale-select', 'value')
            ]
        )(self._update_heatmap_dataframe_json)

        self.app.callback(
            Output('heatmap-debug-json', 'children'),
            [Input('heatmap', 'relayoutData')]
        )(self._update_heatmap_debug_json)

    def _update_heatmap_debug_json(self, input):
        return json.dumps(input)

    def _search_to_ids_json(self, input):
        ids = self._genes_index.search(input)
        return json.dumps(ids)

    def _scatter_to_gene_ids_json(self, input):
        ids = list({
            x['text']
            for x in input['points']
        }) if input else self._genes
        return json.dumps(ids)

    def _scatter_to_condition_ids_json(self, input):
        ids = list({
            x['text']
            for x in input['points']
        }) if input else self._conditions
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

    def _update_heatmap_dataframe_json(
            self,
            selected_conditions_ids_json,
            selected_gene_ids_json,
            scale):
        selected_conditions = (
            json.loads(selected_conditions_ids_json)
            or self._conditions)
        selected_conditions_df = self._union_dataframe[selected_conditions]
        selected_conditions_genes_df = self._filter_by_gene_ids_json(
            selected_conditions_df,
            selected_gene_ids_json
        )
        truncated_dataframe = (
            sort_by_variance(selected_conditions_genes_df)
                .head(self._most_variable_rows)
            if self._most_variable_rows else selected_conditions_genes_df
        )
        cluster_dataframe = cluster(
            truncated_dataframe,
            cluster_rows=self._cluster_rows,
            cluster_cols=self._cluster_cols)

        return json.dumps({
            'cols': cluster_dataframe.columns.tolist(),
            'rows': cluster_dataframe.index.tolist(),
            'matrix': cluster_dataframe.as_matrix().tolist(),
        })

    def _update_heatmap(
            self,
            selected_conditions_ids_json,
            selected_gene_ids_json,
            scale):
        selected_conditions = (
            json.loads(selected_conditions_ids_json)
            or self._conditions)
        selected_conditions_df = self._union_dataframe[selected_conditions]
        selected_conditions_genes_df = self._filter_by_gene_ids_json(
            selected_conditions_df,
            selected_gene_ids_json
        )
        truncated_dataframe = (
            sort_by_variance(selected_conditions_genes_df)
            .head(self._most_variable_rows)
            if self._most_variable_rows else selected_conditions_genes_df
        )
        cluster_dataframe = cluster(
            truncated_dataframe,
            cluster_rows=self._cluster_rows,
            cluster_cols=self._cluster_cols)

        show_genes = len(cluster_dataframe.index.tolist()) < 40

        char_width = 10  # With a proportional font, this is only an estimate.

        if show_genes:
            row_max = max([len(s) for s in list(cluster_dataframe.index)])
            left_margin = row_max * char_width
        else:
            left_margin = 75

        col_max = max([len(s) for s in list(cluster_dataframe)])
        bottom_margin = col_max * char_width
        return {
            'data': [
                self._heatmap(cluster_dataframe, scale == 'log')
            ],
            'layout': go.Layout(
                xaxis={'ticks': '', 'tickangle': 90},
                yaxis={'ticks': '', 'showticklabels': show_genes},
                margin={'l': left_margin, 'b': bottom_margin, 't': 30, 'r': 0}
                # Need top margin so infobox on hover is not truncated
            )
        }

    def _heatmap(self, dataframe, is_log_scale):
        if is_log_scale:
            values = [x for x in dataframe.values.flatten() if x > 0]
            # We will take the log, so exclude zeros.
            adjusted_color_scale = _log_interpolate(
                self._color_scale,
                min(values),
                max(values))
        else:
            adjusted_color_scale = _linear(self._color_scale)

        return go.Heatmap(  # TODO: Non-fuzzy Heatmapgl
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

    def _list_html(self, list):
        """
        Given a dataframe,
        returns the indexes of the dataframe as a single column html table.
        """
        return self._css_url_html() + _remove_rowname_header(
            pandas.DataFrame(list).to_html(
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
