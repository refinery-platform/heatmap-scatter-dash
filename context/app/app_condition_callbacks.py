import json

import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

from app.app_layout import AppLayout
from app.utils.callbacks import (ScatterLayout, dark_dot, figure_output,
                                 light_dot, scatter_inputs)


class AppConditionCallbacks(AppLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app.callback(
            figure_output('scatter-pca'),
            scatter_inputs('pca')
        )(self._update_scatter_pca)

        self.app.callback(
            Output('ids-iframe', 'srcDoc'),
            [Input('scatter-pca', 'selectedData')]
        )(self._update_condition_list)

    def _update_scatter_pca(self, x_axis, y_axis):
        return {
            'data': [
                go.Scattergl(
                    x=self._dataframe_pca[x_axis],
                    y=self._dataframe_pca[y_axis],
                    mode='markers',
                    text=self._dataframe_pca.index,
                    marker=dark_dot
                )
            ],
            'layout': ScatterLayout(x_axis, y_axis)
        }

    def _update_condition_list(self, selected_data):
        points = [point['pointNumber'] for point in selected_data['points']]
        return self._list_html(self._dataframe.T.iloc[points])
        # Alternatively:
        #   pandas.DataFrame(self._dataframe.columns.tolist())
        # but transpose may be more efficient than creating a new DataFrame.
