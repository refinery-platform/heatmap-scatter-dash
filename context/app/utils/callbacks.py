import pandas
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


_light = 'rgb(127,216,127)'
_dark = 'rgb(0,0,127)'

_dark_dot = {
    'color': _dark, 'size': 5
}
_light_dot = {
    'color': _light, 'size': 5
}
_big_dark_dot = {
    'color': _dark, 'size': 5, 'symbol': 'square'
}
_big_light_dot = {
    'color': _light, 'size': 5, 'symbol': 'square'
}


def traces_all_selected(x_axis, y_axis, everyone, selected,
                        highlight=pandas.DataFrame(),
                        selected_highlight=pandas.DataFrame()):
    trace_defs = [
        {
            # Not strictly true that these are "unselected", but the duplicates
            # are obscured by the selected points, and taking the set
            # compliment is not worth the trouble.
            'name': 'unselected',
            'dataframe': everyone,
            'marker': _light_dot,
            'text': None
        },
        {
            'name': 'selected',
            'dataframe': selected,
            'marker': _dark_dot,
            'text': None
        },
        {
            'name': 'gene axis',
            'dataframe': highlight,
            'marker': _big_light_dot,
            'text': highlight.index
        },
        {
            'name': 'gene axis',
            'dataframe': selected_highlight,
            'marker': _big_dark_dot,
            'text': selected_highlight.index
        }
    ]
    labelled = not highlight.empty
    kwargs_list = [
        {
            'x': trace['dataframe'][x_axis],
            'y': trace['dataframe'][y_axis],
            'mode': 'markers',
            'text': trace['text'],
            'marker': trace['marker'],
            'name': trace['name']
        } for trace in trace_defs if not trace['dataframe'].empty
        # Was hitting something like
        # https://community.plot.ly/t/7329
        # when I included the empty df,
        # but I couldn't create a minimal reproducer.
    ]
    if labelled:
        for kwargs in kwargs_list:
            kwargs['textposition'] = 'bottom_center'
            kwargs['hoverinfo'] = 'none'
            kwargs['mode'] = 'markers+text'
    return [
        (go.Scatter if labelled else go.Scattergl)(**kwargs)
        for kwargs in kwargs_list
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
