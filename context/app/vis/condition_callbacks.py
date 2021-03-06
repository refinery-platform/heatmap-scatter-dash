import json

from dash.dependencies import Input, Output

from app.utils.callbacks import (ScatterLayout, figure_output, scatter_inputs,
                                 traces_all_selected)
from app.utils.color import palettes
from app.vis.layout import VisLayout


class VisConditionCallbacks(VisLayout):
    # Since there is only one control here, all the timestamp machinery in
    # AppGeneCallbacks would be excessive, but we might need it some day.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app.callback(
            figure_output('scatter-pca'),
            [Input('selected-conditions-ids-json', 'children')] +
            [Input('palette-select', 'value')] +
            scatter_inputs('sample-by-sample') +
            scatter_inputs('pca',
                           meta_select=not self._meta_dataframe.empty)
        )(self._update_scatter_pca)

        self.app.callback(
            Output('ids-iframe', 'srcDoc'),
            [Input('scatter-pca', 'selectedData')]
        )(self._update_condition_list)

        self.app.callback(
            Output('selected-conditions-ids-json', 'children'),
            [Input('scatter-pca', 'selectedData')]
        )(self._scatter_to_condition_ids_json)

    def _update_scatter_pca(
            self, selected_conditions_ids_json,
            palette_name,
            gene_x_axis, gene_y_axis,
            x_axis, y_axis, selected_metadata=None):
        everyone = self._pca_dataframe
        selected = self._filter_by_condition_ids_json(
            everyone,
            selected_conditions_ids_json
        )
        highlight = everyone.loc[[gene_x_axis, gene_y_axis]]
        selected_highlight = everyone.loc[
            list(set(selected.index) & set(highlight.index))
        ]  # pandas.merge loses the index, sadly, so this is a hack.
        data = traces_all_selected(
            x_axis, y_axis, everyone, selected,
            highlight=highlight,
            selected_highlight=selected_highlight,
            color_by=None if self._meta_dataframe.empty
            else self._meta_dataframe[selected_metadata],
            palette=palettes[palette_name])
        return {
            'data': data,
            'layout': ScatterLayout(x_axis, y_axis)
        }

    def _update_condition_list(self, selected_data):
        conditions = (
            # There are repeats in selected_data, so use set comprehension.
            list({point['text'] for point in selected_data['points']})
            if selected_data else []
        )
        return self._list_html(conditions)
        # Alternatively:
        #   pandas.DataFrame(self._dataframe.columns.tolist())
        # but transpose may be more efficient than a new DataFrame?

    def _filter_by_condition_ids_json(self, dataframe, json_list):
        selected_conditions_ids = json.loads(json_list)
        return dataframe.loc[selected_conditions_ids]
