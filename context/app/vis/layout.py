import dash_core_components as dcc
import dash_html_components as html

from app.utils.color import palettes
from app.utils.resource_loader import ResourceLoader
from app.vis.base import VisBase


class VisLayout(VisBase, ResourceLoader):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_resources()
        self._add_dom()

    def _add_dom(self):
        list_of_sets = [set(df.columns.tolist())
                        for df in self._diff_dataframes.values()]
        diff_heads = ({} if not list_of_sets
                      else set.intersection(*list_of_sets))

        conditions_options = _lv_pairs(self._conditions)
        pc_options = _lv_pairs(['pc1', 'pc2', 'pc3', 'pc4'])
        volcano_options = _lv_pairs(sorted(diff_heads, reverse=True))
        self.scale_options = _lv_pairs(['log', 'linear'])
        self.palette_options = _lv_pairs(palettes.keys())
        self.cluster_options = _lv_pairs(['cluster', 'no cluster'])
        self.label_options = _lv_pairs(['always', 'never', 'auto'])
        self.file_options = _lv_pairs(self._diff_dataframes)

        self.app.layout = html.Div([
            dcc.Location(id='location', refresh=False),  # Not rendered
            html.Div([
                html.Div(
                    self._left_column(),
                    className='col-xs-6'),
                html.Div(
                    self._right_column(
                        pc_options=pc_options,
                        conditions_options=conditions_options,
                        volcano_options=volcano_options),
                    className='col-xs-6')
            ], className='row'),
            self._hidden_div()
        ], className='container-fluid')

    def _left_column(self):
        return [
            dcc.Graph(
                id='heatmap',
                style={'height': '90vh'}
            ),
            html.Div([
                html.Div([
                    html.Label(['gene'],
                               className='col-xs-1 control-label'
                               ),
                    html.Div([
                        dcc.Input(
                            id='search-genes',
                            placeholder='search...',
                            type="text",
                            className='form-control')
                    ], className='col-xs-5'),
                ], className='form-group'),
            ], className='form-horizontal')
        ]

    def _right_column(self, pc_options, conditions_options, volcano_options):
        return [
            html.Br(),  # Top of tab was right against window top

            _tabs('Conditions:', 'PCA', 'IDs', 'Options', help_button=True),
            html.Div([
                self._scatter('pca', pc_options, active=True),
                _iframe('ids'),
                self._options_div('options')
            ], className='tab-content'),

            _tabs('Genes:', 'Sample-by-Sample', 'Volcano', 'Table', 'List'),
            html.Div([
                self._scatter('sample-by-sample',
                              conditions_options, active=True),
                self._scatter('volcano',
                              volcano_options, volcano=True),
                _iframe('table'),
                _iframe('list')
            ], className='tab-content'),
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

    def _options_div(self, id):
        nodes = [
            html.Div([
                dcc.Markdown(
                    '**Colors:** Selecting log scale will also update the '
                    'axes of the scatter plot.'),
                html.Div(
                    _label_dropdown(
                        'scale', 'scale-select', self.scale_options) +
                    _label_dropdown(
                        'palette', 'palette-select', self.palette_options),
                    className='form-group'),
                dcc.Markdown(
                    '**Clustering:** After selecting points in the '
                    'scatterplots, should the heatmap be reclustered? '
                    'This may make rendering slower, and rows and '
                    'columns may be reordered between views.'),
                html.Div(
                    _label_dropdown(
                        'rows', 'cluster-rows-select', self.cluster_options) +
                    _label_dropdown(
                        'cols', 'cluster-cols-select', self.cluster_options),
                    className='form-group'),
                dcc.Markdown(
                    '**Labels:** Row and column labels can be applied '
                    '`always`, `never`, or `automatically`, if there is '
                    'sufficient space.'),
                html.Div(
                    _label_dropdown(
                        'rows', 'label-rows-select', self.label_options) +
                    _label_dropdown(
                        'cols', 'label-cols-select', self.label_options),
                    className='form-group'),
            ], className='form-horizontal')
        ]
        return html.Div(nodes, className='tab-pane',
                        id=id, style={'height': '40vh'})

    def _scatter(self, id, options, active=False, volcano=False):
        dropdowns = [
            _dropdown(id, options, 'x', 0),
            _dropdown(id, options, 'y', 1)
        ]
        if volcano:
            dropdowns.append(
                html.Label(['file'], className='col-xs-1 control-label')
            )
            dropdowns.append(
                dcc.Dropdown(
                    id='file-select',
                    options=self.file_options,
                    value=self.file_options[0]['value']
                    if self.file_options else None,
                    className='col-xs-11'
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
                    'width': '45vw'
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


def _lv_pairs(opts):
    return [
        {'label': opt, 'value': opt}
        for opt in opts
    ]


def _label_dropdown(label, id, options):
    # Returns a two element list
    return [
        html.Label([label],
                   className='col-xs-1 control-label'),
        dcc.Dropdown(
            id=id,
            options=options,
            className='col-xs-5'
        )
    ]


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


def _dropdown(id, options, axis, axis_index):
    if options:
        value = options[axis_index]['value']
    else:
        value = None
    return html.Span(
        [
            html.Label(
                [axis],
                className='col-xs-1 control-label'
            ),
            dcc.Dropdown(
                id='scatter-{}-{}-axis-select'.format(id, axis),
                options=options,
                value=value,
                className='col-xs-5'
            )
        ]
    )


def _class_from_index(i):
    if i == 0:
        # The first "tab" is really just a label.
        return 'disabled'
    if i == 1:
        return 'active'
    return ''


def _tabs(*names, help_button=False):
    li_list = [
        html.Li([
            html.A([
                name
            ], href='#' + name.lower())
        ], className=_class_from_index(index))
        for (index, name) in enumerate(names)
    ]

    css_classes = 'btn pull-right'
    if help_button:
        li_list.append(html.A(
            ['Help'], href='help',
            target='_blank',
            className=css_classes
        ))
        li_list.append(html.A(
            ['Report Bug'], href='https://github.com/refinery-platform/'
            'heatmap-scatter-dash/issues/new',
            target='_blank',
            className=css_classes
        ))
    tabs = html.Ul(li_list,
                   className='nav nav-tabs')
    return tabs
