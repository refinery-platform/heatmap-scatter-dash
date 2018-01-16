import dash
import dash_html_components as html
import dash_core_components as dcc

from app.resource_loader import ResourceLoader

class HelpApp(ResourceLoader):

    def __init__(self,
                 server=None,
                 url_base_pathname=None,
                 api_prefix=None):
        self.app = dash.Dash(server=server,
                             url_base_pathname=url_base_pathname)
        self.load_resources()

        if api_prefix:
            self.app.config.update({
                'requests_pathname_prefix': api_prefix
            })
        self.app.title = 'Heatmap + Scatterplots: Help'

        self.app.layout = html.Div([
            html.Div([
                dcc.Markdown([
'''
# Help

This is a test
'''
                ], className='col-md-12'),
            ], className='row'),
        ], className='container')
