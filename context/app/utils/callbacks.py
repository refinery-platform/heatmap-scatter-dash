import pandas
import plotly.graph_objs as go
from dash.dependencies import Input, Output


def figure_output(element_id):
    return Output(element_id, 'figure')


def scatter_inputs(element_id, scale_select=False, meta_select=False):
    inputs = [
        Input('scatter-{}-{}-axis-select'.format(element_id, axis), 'value')
        for axis in ['x', 'y']
    ]
    if scale_select:
        inputs.append(Input('scale-select', 'value'))
    if meta_select:
        inputs.append(Input('meta-select', 'value'))
    return inputs


_light = 'rgb(200,200,200)'
_dark = 'rgb(0,0,127)'

_dark_dot = {
    'color': _dark, 'size': 5
}
_light_dot = {
    'color': _light, 'size': 5
}
_big_dark_dot = {
    'color': _dark, 'size': 10
}
_big_light_dot = {
    'color': _light, 'size': 10
}


def traces_all_selected(x_axis, y_axis, everyone, selected,
                        highlight=pandas.DataFrame(),
                        selected_highlight=pandas.DataFrame(),
                        color_by=None, palette=None):
    # Was hitting something like
    # https://community.plot.ly/t/7329
    # when I included the empty df,
    # but I couldn't create a minimal reproducer.
    trace_defs = [
        {
            # Not strictly true that these are "unselected", but the duplicates
            # are obscured by the selected points, and taking the set
            # compliment is not worth the trouble.
            'name': 'unselected',
            'dataframe': everyone,
            'marker': _light_dot
        },
        {
            'name': 'gene axis',
            'dataframe': highlight,
            'marker': _big_light_dot
        },
        {
            'name': 'selected',
            'dataframe': selected,
            'marker': _dark_dot if color_by is None else {
                'color': color_by,
                'size': 5,
                'colorscale': palette.linear()
            }
        },
        {
            'name': 'gene axis',
            'dataframe': selected_highlight,
            'marker': _big_dark_dot if color_by is None else {
                'color': color_by,
                'size': 10,
                'colorscale': palette.linear()
            }
        }
    ]
    return [
        go.Scattergl(
            x=trace['dataframe'][x_axis],
            y=trace['dataframe'][y_axis],
            mode='markers',
            text=trace['dataframe'].index,
            marker=trace['marker'],
            name=trace['name']
        ) for trace in trace_defs
        if not trace['dataframe'].empty
        # If there are only two samples,
        # there will be only one principle component.
        # Might need more messaging to user here?
        and x_axis in trace['dataframe']
        and y_axis in trace['dataframe']
    ]


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
            dragmode='select',
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
