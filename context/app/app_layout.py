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
            self.app.css.append_css({'external_url': url})

    def _add_scripts(self):
        for url in self._js_urls:
            self.app.scripts.append_script({'external_url': url})

    def _add_dom(self):
        conditions_options = [
            {'label': cond, 'value': cond}
            for cond in self._conditions
        ]

        pc_options = [
            {'label': pc, 'value': pc}
            for pc in ['pc1', 'pc2', 'pc3', 'pc4']  # TODO: DRY
        ]

        list_of_sets = [set(df.columns.tolist())
                        for df in self._diff_dataframes.values()]
        diff_heads = ({} if not list_of_sets
                      else set.intersection(*list_of_sets))
        volcano_options = [
            {'label': diff_head, 'value': diff_head}
            for diff_head in sorted(diff_heads, reverse=True)
            # reversed, because the y axis label begins with "-"
        ]

        self.scale_options = [
            {'label': scale, 'value': scale}
            for scale in ['log', 'linear']
        ]

        self.file_options = [
            {'label': file, 'value': file}
            for file in self._diff_dataframes
        ]

        self.app.layout = html.Div([
            html.Div([
                html.Div(
                    self._left_column(),
                    className='col-md-6'),
                html.Div(
                    self._right_column(
                        pc_options=pc_options,
                        conditions_options=conditions_options,
                        volcano_options=volcano_options),
                    className='col-md-6')
            ], className='row'),
            self._hidden_div()
        ], className='container')

    def _left_column(self):
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
                        options=self.scale_options,
                        value='log',
                        className='col-sm-5'
                    )
                ], className='form-group'),
            ], className='form-horizontal'),
            html.Div(id='heatmap-debug-json'),
            html.Div(id='heatmap-dataframe-json')
        ]

    def _right_column(self, pc_options, conditions_options, volcano_options):
        return [
            html.Br(),  # Top of tab was right against window top

            _tabs('Conditions:', 'PCA', 'IDs'),
            html.Div([
                self._scatter('pca', pc_options, active=True),
                _iframe('ids')
            ], className='tab-content'),

            _tabs('Genes:', 'Sample-by-Sample', 'Volcano', 'Table', 'List'),
            html.Div([
                self._scatter('sample-by-sample',
                              conditions_options, active=True),
                self._scatter('volcano',
                              volcano_options, volcano=True),
                _iframe('table'),
                _iframe('list')
            ], className='tab-content')
        ]

    def _hidden_div(self):
        return html.Div(
            [
                html.Hr(),

                html.B(['selected-conditions:']),
                html.Div(id='selected-conditions-ids-json'),

                html.Hr(),

                html.B(['search-genes:']),
                html.Div(id='search-genes-timestamp'),
                html.Div(id='search-genes-ids-json'),
                html.B(['scatter-sample-by-sample:']),
                html.Div(id='scatter-sample-by-sample-timestamp'),
                html.Div(id='scatter-sample-by-sample-ids-json'),
                html.B(['scatter-volcano:']),
                html.Div(id='scatter-volcano-timestamp'),
                html.Div(id='scatter-volcano-ids-json'),
                html.B(['selected-genes:']),
                html.Div(id='selected-genes-ids-json')
            ],
            style={'display': 'block' if self._debug else 'none'}
        )

    def _scatter(self, id, options, active=False, volcano=False):
        dropdowns = [
            _dropdown(id, options, 'x', 0),
            _dropdown(id, options, 'y', 1)
        ]
        if volcano:
            dropdowns.append(
                html.Label(['file'], className='col-sm-1 control-label')
            )
            dropdowns.append(
                dcc.Dropdown(
                    id='file-select',
                    options=self.file_options,
                    value=self.file_options[0]['value']
                    if self.file_options else None,
                    className='col-sm-11'
                ))
            # TODO: scale selector for volcano?
        control_nodes = [
            html.Div(dropdowns, className='form-group')
        ]
        nodes = [
            dcc.Graph(
                id='scatter-{}'.format(id),
                style={
                    'height': '33vh',
                    'width': '40vw'
                    # Shouldn't need to specify manually, but
                    # volcano was not getting the correct horizontal sizing...
                    # maybe because it's not on the screen at load time?
                }
            ),
            html.Div(control_nodes, className='form-horizontal')
        ]
        className = 'tab-pane'
        if active:
            className += ' active'
        return html.Div(nodes, className=className, id=id)


def _iframe(id):
    return html.Div([
        html.Br(),
        html.Iframe(id=id + '-iframe',
                    srcDoc='First select a subset')
        # or
        #   dcc.Graph(id='gene-table',
        #   figure=ff.create_table(self._union_dataframe.to_html()))
        #   (but that's slow)
        # or
        #   https://community.plot.ly/t/display-tables-in-dash/4707/13
    ], className='tab-pane', id=id)


def _dropdown(id, options, axis, axis_index, full_width=False):
    if options:
        value = options[axis_index]['value']
    else:
        value = None
    return html.Span(
        [
            html.Label(
                [axis],
                className='col-sm-1 control-label'
            ),
            dcc.Dropdown(
                id='scatter-{}-{}-axis-select'.format(id, axis),
                options=options,
                value=value,
                className='col-sm-11' if full_width else 'col-sm-5'
            )
        ]
    )


def _class_from_index(i):
    if i == 0:
        return 'disabled'
    if i == 1:
        return 'active'
    return ''


def _tabs(*names):
    tabs = html.Ul([
        html.Li([
            html.A([
                name
            ], href='#' + name.lower())
        ], className=_class_from_index(index))
        for (index, name) in enumerate(names)],
        className='nav nav-tabs')
    return tabs
