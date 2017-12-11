
import dash_core_components as dcc
import dash_html_components as html
from base64 import urlsafe_b64encode


def _to_data_uri(s):
    uri = (
        'data:application/javascript;base64,'.encode('utf8') +
        urlsafe_b64encode(s.encode('utf8'))
    ).decode("utf-8", "strict")
    return uri


def dropdown(id, options, axis, axis_index):
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


def scatter(id, options, search=False, log=False):
    control_nodes = [
        html.Div([
            dropdown(id, options, 'x', 0),
            dropdown(id, options, 'y', 1)
        ],
            className='form-group')
    ]
    if search:
        control_nodes.append(html.Div([
            html.Label(
                ['gene'],
                className='col-sm-1 control-label'
            ),
            html.Div([
                dcc.Input(
                    id='search-{}'.format(id),
                    placeholder='search...',
                    type="text",
                    className='form-control')
            ],
                className='col-sm-11')
        ],
            className='form-group'))
    nodes = [
        dcc.Graph(
            id='scatter-{}'.format(id),
            style={'height': '33vh'}
        ),
        html.Div(control_nodes, className='form-horizontal')
    ]
    return html.Div(nodes, className='tab-pane active', id=id)

def tabs(*names):
    tabs = html.Ul([
        html.Li([
            html.A([
                name
            ], href='#'+name.lower())
        ], className=('active' if index==0 else ''))
        for (index, name) in enumerate(names)],
        className='nav nav-tabs')
    return tabs


def configure_layout(app_wrapper):
    app_wrapper.app.css.append_css({
        'external_url':
            'https://maxcdn.bootstrapcdn.com/'
            'bootstrap/3.3.7/css/bootstrap.min.css'
    })
    app_wrapper.app.scripts.append_script({
        'external_url':
            'https://code.jquery.com/jquery-3.1.1.slim.min.js'
    })
    app_wrapper.app.scripts.append_script({
        'external_url':
            'https://maxcdn.bootstrapcdn.com/'
            'bootstrap/3.3.7/js/bootstrap.min.js'
    })
    app_wrapper.app.scripts.append_script({
        'external_url':
            'https://maxcdn.bootstrapcdn.com/'
            'bootstrap/3.3.7/js/bootstrap.min.js'
    })
    app_wrapper.app.scripts.append_script({
        'external_url': _to_data_uri("""
            $('body').on('click', '.nav-tabs a', function(e) {
                e.preventDefault();
                $(this).tab('show');
            });""")
        # TODO: This is not good.
        # Currently, there is no way to get data attributes in Dash.
        # https://community.plot.ly/t/can-data-attributes-be-created-in-dash/7222
        # So, we need to register them by hand...
        # but when the JS loads, React hasn't yet
        # generated the DOM, so we use "on" instead.
    })

    conditions_options = [
        {'label': cond, 'value': cond}
        for cond in app_wrapper._conditions
    ]

    pc_options = [
        {'label': pc, 'value': pc}
        for pc in ['pc1', 'pc2', 'pc3', 'pc4']  # TODO: DRY
    ]

    app_wrapper.app.layout = html.Div([
        html.Div([
            html.Div([
                dcc.Graph(
                    id='heatmap',
                    style={'height': '100vh'}
                ),
            ],
                className='col-md-6'),
            html.Div([
                html.Br(),  # Top of tab was right against window top
                tabs('PCA'),
                html.Div([
                    scatter('pca', pc_options),
                ]),
                tabs('Genes', 'Volcano'),
                html.Div([
                    scatter('genes', conditions_options, search=True),
                    scatter('volcano', conditions_options)
                ], className='tab-content')
            ], className='col-md-6')
        ], className='row')
    ], className='container')