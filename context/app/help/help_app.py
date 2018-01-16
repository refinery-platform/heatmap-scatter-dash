import dash
import dash_html_components as html


class HelpApp():

    def __init__(self,
                 server=None,
                 url_base_pathname=None,
                 api_prefix=None):
        self.app = dash.Dash(server=server,
                             url_base_pathname=url_base_pathname)
        if api_prefix:
            self.app.config.update({
                'requests_pathname_prefix': api_prefix
            })
        self.app.title = 'Heatmap + Scatterplots: Help'

        self.app.layout = html.Div([
            html.Div([
                html.Div([
                    'help???'
                ], className='col-md-6'),
            ], className='row'),
        ], className='container')
