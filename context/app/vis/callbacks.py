import json
import re
import time

import pandas
import plotly.graph_objs as go
from dash.dependencies import Input

from app.utils.callbacks import figure_output
from app.utils.cluster import cluster
from app.utils.frames import sort_by_variance
from app.vis.condition_callbacks import VisConditionCallbacks
from app.vis.gene_callbacks import VisGeneCallbacks


class VisCallbacks(VisGeneCallbacks, VisConditionCallbacks):
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

    def _update_heatmap(
            self,
            selected_conditions_ids_json,
            selected_gene_ids_json,
            scale):
        with self._profiler():
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

            # With a proportional font, this is only an estimate.
            char_width = 10

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
                    margin={'l': left_margin,
                            'b': bottom_margin, 't': 30, 'r': 0}
                    # Need top margin so infobox on hover is not truncated
                )
            }

    def _heatmap(self, dataframe, is_log_scale):
        if is_log_scale:
            values = [x for x in dataframe.values.flatten() if x > 0]
            # We will take the log, so exclude zeros.
            adjusted_color_scale = \
                self._color_scale.log(min(values), max(values))
        else:
            adjusted_color_scale = \
                self._color_scale.linear()

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
