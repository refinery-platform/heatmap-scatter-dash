import os

import dash
import dash_core_components as dcc
import dash_html_components as html

from app.utils.resource_loader import ResourceLoader


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

        with open(relative_path('help.md')) as f:
            markdown = f.read()

        self.app.layout = html.Div([
            html.Div([
                dcc.Markdown([
                    markdown
                ], className='col-md-12'),
            ], className='row'),
        ], className='container-fluid')


def relative_path(file):
    # https://stackoverflow.com/questions/4060221 for more options
    return os.path.join(os.path.dirname(__file__), file)
