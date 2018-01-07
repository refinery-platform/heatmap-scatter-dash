import json

from dash.dependencies import Input, Output

from app.app_layout import AppLayout
from app.utils.callbacks import (ScatterLayout, dark_dot, figure_output,
                                 light_dot, scatter_inputs, traces)


class AppConditionCallbacks(AppLayout):
    # Since there is only one control here, all the timestamp machinery in
    # AppGeneCallbacks would be excessive, but we might need it some day.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app.callback(
            figure_output('scatter-pca'),
            [Input('selected-conditions-ids-json', 'children')] +
            scatter_inputs('pca')
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
            self, selected_conditions_ids_json, x_axis, y_axis):
        all = self._pca_dataframe
        selected = self._filter_by_condition_ids_json(
            all,
            selected_conditions_ids_json
        )
        data = traces(x_axis, y_axis, [(all, light_dot), (selected, dark_dot)])
        return {
            'data': data,
            'layout': ScatterLayout(x_axis, y_axis)
        }

    def _update_condition_list(self, selected_data):
        self.info('_update_condition_list', selected_data)
        conditions = (
            # There are repeats in selected_data, so use set comprehension.
            list({point['text'] for point in selected_data['points']})
            if selected_data else []
        )
        return self._list_html(self._union_dataframe.T.loc[conditions])
        # Alternatively:
        #   pandas.DataFrame(self._dataframe.columns.tolist())
        # but transpose may be more efficient than creating a new DataFrame.

    def _filter_by_condition_ids_json(self, dataframe, json_list):
        selected_conditions_ids = json.loads(json_list)
        return dataframe.loc[selected_conditions_ids]
