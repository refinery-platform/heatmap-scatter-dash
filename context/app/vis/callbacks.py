import html
import json
import re
import time
from urllib.parse import parse_qs, urlencode, urlparse

import plotly.graph_objs as go
from dash.dependencies import Input, Output

from app.utils.callbacks import figure_output
from app.utils.cluster import cluster
from app.utils.color import palettes
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
                Input('scale-select', 'value'),
                Input('palette-select', 'value'),
                Input('cluster-rows-select', 'value'),
                Input('cluster-cols-select', 'value'),
                Input('label-rows-select', 'value'),
                Input('label-cols-select', 'value'),
                Input('scaling-select', 'value')
            ]
        )(self._update_heatmap)

        url_keys = _DEFAULTS.keys()
        self._write_query_callback(url_keys)
        for key in url_keys:
            self._read_query_callback(key)

    def _read_query_callback(self, key):
        # Registers a callback which fills in a selector
        # with a value from the url query.
        self.app.callback(
            Output(key + '-select', 'value'),
            [Input('location', component_property='href')]
        )(lambda query: _parse_url(query, key))

    def _write_query_callback(self, keys):
        # We read from location.href and write to location.search
        # to avoid an infinite loop.
        self.app.callback(
            Output('location', 'search'),
            [Input(key + '-select', 'value') for key in keys]
        )(lambda *args: '?' + urlencode(
            {key: args[i] for (i, key) in enumerate(keys)}
        ))

    def _search_to_ids_json(self, search_input):
        ids = self._genes_index.search(search_input)
        return json.dumps(ids)

    def _scatter_to_gene_ids_json(self, scatter_input):
        ids = list({
            x['text']
            for x in scatter_input['points']
        }) if scatter_input else self._genes
        return json.dumps(ids)

    def _scatter_to_condition_ids_json(self, scatter_input):
        ids = list({
            x['text']
            for x in scatter_input['points']
        }) if scatter_input else self._conditions
        return json.dumps(ids)

    def _update_timestamp(self, unused_input):
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
            scale,
            palette,
            cluster_rows,
            cluster_cols,
            label_rows_mode,
            label_cols_mode,
            row_scaling_mode):
        selected_conditions = (
            json.loads(selected_conditions_ids_json)
            or self._conditions)
        base_df = self._scale_dataframe(row_scaling_mode)
        selected_conditions_df = base_df[selected_conditions]
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
            cluster_rows=(cluster_rows == 'cluster'),
            cluster_cols=(cluster_cols == 'cluster'))

        show_genes = (len(cluster_dataframe.index.tolist()) < 40
                      and label_rows_mode == 'auto') or \
            label_rows_mode == 'always'
        show_conditions = label_cols_mode in ['always', 'auto']

        # With a proportional font, this is only an estimate.
        char_width = 8

        if show_genes:
            row_max = max([len(s) for s in list(self._union_label_map.values())])
            left_margin = row_max * char_width
        else:
            left_margin = 75

        if show_conditions:
            col_max = max([len(s) for s in list(cluster_dataframe)])
            bottom_margin = col_max * char_width
        else:
            bottom_margin = 10

        return {
            'data': [
                self._heatmap(cluster_dataframe,
                              is_log_scale=(scale == 'log'),
                              palette=palettes[palette])
            ],
            'layout': go.Layout(
                xaxis={'ticks': '',
                       'showticklabels': show_conditions,
                       'tickangle': 90,
                       'type': 'category'},
                yaxis={'ticks': '',
                       'showticklabels': show_genes,
                       'type': 'category'},
                margin={'l': left_margin,
                        'b': bottom_margin,
                        't': 30,  # so infobox on hover is not truncated
                        'r': 0}
            )
        }

    def _heatmap(self, dataframe, is_log_scale, palette):
        if is_log_scale:
            values = [x for x in dataframe.values.flatten() if x > 0]
            # We will take the log, so exclude zeros.
            adjusted_color_scale = \
                palette.log(min(values), max(values))
        else:
            adjusted_color_scale = \
                palette.linear()
        return go.Heatmap(  # TODO: Non-fuzzy Heatmapgl
            x=dataframe.columns.tolist(),
            y=[self._union_label_map[i] for i in dataframe.index.tolist()],
            z=dataframe.as_matrix(),
            colorscale=adjusted_color_scale)

    def _table_html(self, dataframe):
        """
        Given a dataframe,
        returns either a preformatted block or an html table.
        """
        # NOTE: There is a different truncated_dataframe for the heatmap.
        # That is 500 rows by default, corresponding to a typical height in
        # pixels. The truncation here could be plausibly more or less.
        if dataframe.empty:
            return ''
        if self._truncate_table and dataframe.shape[0] > self._truncate_table:
            dataframe = dataframe.head(self._truncate_table)
            warning = '<p>Limited to the first {} rows.</p>'.format(
                self._truncate_table)
        else:
            warning = ''
        return self._css_url_html() + warning + (
            _remove_rowname_header(dataframe.to_html())
            if self._html_table
            else '<pre>{}</pre>'.format(html.escape(dataframe.to_string()))
        )

    def _list_html(self, items):
        """
        Given a list,
        wrap it in <pre>.
        """
        return self._css_url_html() + '<pre>{}</pre>'.format('\n'.join(items))

    def _css_url_html(self):
        return ''.join([
            '<link rel="stylesheet" property="stylesheet" href="{}">'
            .format(url) for url in self._css_urls
        ])


def _remove_rowname_header(s):
    return re.sub(r'<tr[^>]*>[^<]*<th>(rowname|0)</th>.*?</tr>', '', s,
                  count=1, flags=re.DOTALL)


_DEFAULTS = {
    'scale': 'log',
    'palette': 'black-white',
    'cluster-rows': 'cluster',
    'cluster-cols': 'cluster',
    'label-rows': 'auto',
    'label-cols': 'auto',
    'scaling': 'no rescale'
}


def _parse_url(url, key):
    if url:
        query = urlparse(url).query
        if query:
            values = parse_qs(query).get(key)
            if values:
                return values[0]
    return _DEFAULTS[key]
