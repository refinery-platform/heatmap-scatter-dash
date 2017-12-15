
from base64 import urlsafe_b64encode

import dash_core_components as dcc
import dash_html_components as html

from app.app_base import AppBase


class AppLayout(AppBase):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._add_css()
        self._add_scripts()
        self._add_dom()

    def _add_css(self):
        for url in self._css_urls:
            self.app.css.append_css({
                'external_url': url
            })
        self.app.css.append_css({
            'external_url': _to_data_uri(
                """
                .plotlyjsicon {
                    display: none;
                }
                iframe {
                    border: none;
                    width: 100%;
                    height: 33vh;
                }
                """,
                "text/css")
        })

    def _add_scripts(self):
        self.app.scripts.append_script({
            'external_url':
                'https://code.jquery.com/'
                'jquery-3.1.1.slim.min.js'
        })
        self.app.scripts.append_script({
            'external_url':
                'https://maxcdn.bootstrapcdn.com/'
                'bootstrap/3.3.7/js/bootstrap.min.js'
        })
        self.app.scripts.append_script({
            'external_url': _to_data_uri("""
                $('body').on('click', '.nav-tabs a', function(e) {
                    e.preventDefault();
                    $(this).tab('show');
                });""", 'application/javascript')
            # TODO: This is not good.
            # Currently, there is no way to get data attributes in Dash.
            # https://community.plot.ly/t/can-data-attributes-be-created-in-dash/7222
            # So, we need to register them by hand...
            # but when the JS loads, React hasn't yet
            # generated the DOM, so we use "on" instead.
            # html.Script() does put an element in the DOM,
            # but it doesn't execute.
        })

    def _add_dom(self):
        conditions_options = [
            {'label': cond, 'value': cond}
            for cond in self._conditions
        ]

        pc_options = [
            {'label': pc, 'value': pc}
            for pc in ['pc1', 'pc2', 'pc3', 'pc4']  # TODO: DRY
        ]

        scale_options = [
            {'label': scale, 'value': scale}
            for scale in ['log', 'linear']
        ]

        self.app.layout = html.Div([
            html.Div([
                html.Div(
                    self._left_column(
                        scale_options=scale_options),
                    className='col-md-6'),
                html.Div(
                    self._right_column(
                        pc_options=pc_options,
                        conditions_options=conditions_options),
                    className='col-md-6')
            ], className='row')
        ], className='container')

    def _left_column(self, scale_options):
        return [
            dcc.Graph(
                id='heatmap',
                style={'height': '90vh'}
            ),
            html.Div([
                html.Div([
                    html.Label(['gene'],
                               className='col-sm-1 control-label'
                               ),
                    html.Div([
                        dcc.Input(
                            id='search-genes',
                            placeholder='search...',
                            type="text",
                            className='form-control')
                    ], className='col-sm-5'),
                    html.Label(['scale'],
                               className='col-sm-1 control-label'
                               ),
                    dcc.Dropdown(
                        id='scale-select',
                        options=scale_options,
                        value='log',
                        className='col-sm-5'
                    )
                ], className='form-group'),
            ], className='form-horizontal')
        ]

    def _right_column(self, pc_options, conditions_options):
        return [
            html.Br(),  # Top of tab was right against window top

            _tabs('PCA'),
            html.Div([
                _scatter('pca', pc_options, active=True),
            ], className='tab-content'),

            _tabs('Genes', 'Volcano', 'Table'),
            html.Div([
                _scatter('genes', conditions_options, active=True),
                _scatter('volcano', conditions_options),
                html.Div([
                    html.Br(),
                    html.Iframe(id='table-iframe',
                                srcDoc='First select a subset')
                    # or
                    #   dcc.Graph(id='gene-table',
                    #   figure=ff.create_table(self._dataframe.to_html()))
                    #   (but that's slow)
                    # or
                    #   https://community.plot.ly/t/display-tables-in-dash/4707/13
                ], className='tab-pane', id='table')
            ], className='tab-content')
        ]


def _to_data_uri(s, mime):
    uri = (
        ('data:' + mime + ';base64,').encode('utf8') +
        urlsafe_b64encode(s.encode('utf8'))
    ).decode("utf-8", "strict")
    return uri


def _dropdown(id, options, axis, axis_index):
    return html.Span(
        [
            html.Label(
                [axis],
                className='col-sm-1 control-label'
            ),
            dcc.Dropdown(
                id='scatter-{}-{}-axis-select'.format(id, axis),
                options=options,
                value=options[axis_index]['value'],
                className='col-sm-5'
            )
        ]
    )


def _scatter(id, options, log=False, active=False):
    control_nodes = [
        html.Div([
            _dropdown(id, options, 'x', 0),
            _dropdown(id, options, 'y', 1)
        ], className='form-group')
    ]
    nodes = [
        dcc.Graph(
            id='scatter-{}'.format(id),
            style={
                'height': '33vh',
                'width': '40vw'
                # Volcano was not getting the correct horizontal sizing...
                # maybe because it's not on the screen at load time?
            }
        ),
        html.Div(control_nodes, className='form-horizontal')
    ]
    className = 'tab-pane'
    if active:
        className += ' active'
    return html.Div(nodes, className=className, id=id)


def _tabs(*names):
    tabs = html.Ul([
        html.Li([
            html.A([
                name
            ], href='#' + name.lower())
        ], className=('active' if index == 0 else ''))
        for (index, name) in enumerate(names)],
        className='nav nav-tabs')
    return tabs
