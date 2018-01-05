import json

import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

from app.app_layout import AppLayout
from app.utils.callbacks import (ScatterLayout, dark_dot, figure_output,
                                 light_dot, scatter_inputs)


class AppGeneCallbacks(AppLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app.callback(
            figure_output('scatter-sample-by-sample'),
            [Input('selected-genes-ids-json', 'children')] +
            scatter_inputs('sample-by-sample', scale_select=True)
        )(self._update_scatter_genes)

        self.app.callback(
            figure_output('scatter-volcano'),
            [Input('selected-genes-ids-json', 'children'),
             Input('file-select', 'value')] +
            scatter_inputs('volcano', scale_select=False)
        )(self._update_scatter_volcano)

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
                    marker=light_dot,
                ),
                go.Scattergl(
                    x=selected[x_axis],
                    y=selected[y_axis],
                    mode='markers',
                    text=selected.index,
                    marker=dark_dot
                )
            ],
            'layout': ScatterLayout(
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
                    marker=light_dot
                ),
                go.Scattergl(
                    x=selected[x_axis],
                    y=selected[y_axis],
                    mode='markers',
                    text=self._dataframe.index,
                    marker=dark_dot
                )
            ],
            'layout': ScatterLayout(x_axis, y_axis)
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