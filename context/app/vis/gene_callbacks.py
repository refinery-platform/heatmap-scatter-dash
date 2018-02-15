import json

from dash.dependencies import Input, Output, State

from app.utils.callbacks import (ScatterLayout, figure_output, scatter_inputs,
                                 traces_all_selected)
from app.vis.layout import VisLayout


class VisGeneCallbacks(VisLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app.callback(
            figure_output('scatter-sample-by-sample'),
            [Input('selected-genes-ids-json', 'children')] +
            scatter_inputs('sample-by-sample', scale_select=True) +
            [Input('scaling-select', 'value')]
        )(self._update_scatter_genes)

        self.app.callback(
            figure_output('scatter-volcano'),
            [Input('selected-genes-ids-json', 'children'),
             Input('file-select', 'value')] +
            scatter_inputs('volcano', scale_select=False)
        )(self._update_scatter_volcano)

        self.app.callback(
            Output('table-iframe', 'srcDoc'),
            [Input('selected-genes-ids-json', 'children'),
             Input('selected-conditions-ids-json', 'children')]
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
        )(self._scatter_to_gene_ids_json)

        self.app.callback(
            Output('scatter-volcano-ids-json', 'children'),
            [Input('scatter-volcano', 'selectedData')]
        )(self._scatter_to_gene_ids_json)

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

    def _update_scatter_genes(
            self,
            selected_gene_ids_json,
            x_axis, y_axis, scale,
            row_scaling_mode):
        with self._profiler():
            is_log = scale == 'log'
            everyone = (
                self._union_dataframe if row_scaling_mode == 'no rescale'
                else self._scaled_dataframe
            )
            selected = self._filter_by_gene_ids_json(
                everyone,
                selected_gene_ids_json
            )
            data = traces_all_selected(x_axis, y_axis, everyone, selected)
            return {
                'data': data,
                'layout': ScatterLayout(
                    x_axis, y_axis,
                    x_log=is_log, y_log=is_log)
            }

    def _update_scatter_volcano(
            self,
            selected_gene_ids_json,
            file_selected,
            x_axis, y_axis):
        with self._profiler():
            if not x_axis:
                # ie, there are no differential files.
                # "file" itself is (mis)used for messaging.
                return {}
            everyone = self._diff_dataframes[file_selected]
            selected = self._filter_by_gene_ids_json(
                everyone,
                selected_gene_ids_json
            )
            data = traces_all_selected(x_axis, y_axis, everyone, selected)
            return {
                'data': data,
                'layout': ScatterLayout(x_axis, y_axis)
            }

    def _update_gene_table(self,
                           selected_gene_ids_json,
                           selected_condition_ids_json):
        with self._profiler():
            selected_genes_df = self._filter_by_gene_ids_json(
                self._union_dataframe,
                selected_gene_ids_json
            )
            selected_conditions = json.loads(selected_condition_ids_json)
            return self._table_html(self._meta_dataframe.T) \
                + self._table_html(selected_genes_df[selected_conditions])

    def _update_gene_list(self, selected_genes_ids_json):
        with self._profiler():
            selected_genes_df = self._filter_by_gene_ids_json(
                self._union_dataframe,
                selected_genes_ids_json
            )
            return self._list_html(selected_genes_df.index)

    def _filter_by_gene_ids_json(self, dataframe, json_list):
        with self._profiler():
            if json_list:
                selected_gene_ids = json.loads(json_list)
                return dataframe.reindex(selected_gene_ids)
            else:
                return dataframe
