from dash.dependencies import Input
from app.app_layout import AppLayout
from app.utils.callbacks import figure_output, scatter_inputs

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