import plotly.graph_objs as go
from dash.dependencies import Input, Output


def figure_output(id):
    return Output(id, 'figure')


def scatter_inputs(id, scale_select=False):
    inputs = [
        Input('scatter-{}-{}-axis-select'.format(id, axis), 'value')
        for axis in ['x', 'y']
    ]
    if scale_select:
        inputs.append(
            Input('scale-select', 'value')
        )
    return inputs


dark_dot = {
    'color': 'rgb(0,0,127)',
    'size': 5
}
light_dot = {
    'color': 'rgb(127,216,127)',
    'size': 5
}


class ScatterLayout(go.Layout):
    def __init__(self, x_axis, y_axis, x_log=False, y_log=False):
        x_axis_config = {'title': x_axis}
        y_axis_config = {'title': y_axis}
        if x_log:
            x_axis_config['type'] = 'log'
        if y_log:
            y_axis_config['type'] = 'log'
        super().__init__(
            showlegend=False,
            xaxis=x_axis_config,
            yaxis=y_axis_config,
            margin=go.Margin(
                l=80,  # noqa: E741
                r=20,
                b=60,
                t=20,
                pad=5
            )
        )
