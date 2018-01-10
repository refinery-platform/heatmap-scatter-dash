from base64 import urlsafe_b64encode
import os

import dash
import pandas
from plotly.figure_factory.utils import PLOTLY_SCALES

from app.utils.pca import pca
from app.utils.search import SimpleIndex


class AppBase:

    def __init__(self,
                 union_dataframe,
                 diff_dataframes={'none given': pandas.DataFrame()},
                 colors='Greys',
                 reverse_colors=False,
                 heatmap_type='svg',
                 top_rows=500,
                 cluster_rows=False,
                 cluster_cols=False,
                 api_prefix=None,
                 debug=False):
        self._top_rows = top_rows
        self._cluster_rows = cluster_rows
        self._cluster_cols = cluster_cols
        self._union_dataframe = union_dataframe
        self._pca_dataframe = pca(self._union_dataframe)
        self._diff_dataframes = diff_dataframes
        self._conditions = self._union_dataframe.axes[1].tolist()
        self._genes = self._union_dataframe.axes[0].tolist()
        self._genes_index = SimpleIndex()
        for gene in self._genes:
            self._genes_index.add(gene)
        if reverse_colors:
            self._color_scale = list(reversed(PLOTLY_SCALES[colors]))
        else:
            self._color_scale = PLOTLY_SCALES[colors]
        self._heatmap_type = heatmap_type
        with open(relative_path('extra.css')) as extra_css_file:
            self._css_urls = [
                'https://maxcdn.bootstrapcdn.com/'
                    'bootstrap/3.3.7/css/bootstrap.min.css',
                to_data_uri(extra_css_file.read(), 'text/css')
            ]
        with open(relative_path('extra.js')) as extra_js_file:
            self._js_urls = [
                'https://code.jquery.com/'
                    'jquery-3.1.1.slim.min.js',
                'https://maxcdn.bootstrapcdn.com/'
                    'bootstrap/3.3.7/js/bootstrap.min.js',
                to_data_uri(extra_js_file.read(),
                    'application/javascript')
            ]
        self._debug = debug
        self.app = dash.Dash()
        if api_prefix:
            self.app.config.update({
                'requests_pathname_prefix': api_prefix
            })
        self.app.title = 'Heatmap + Scatterplots'
        # Works, but not officially supported:
        # https://community.plot.ly/t/including-page-titles-favicon-etc-in-dash-app/4648

    def info(self, *fields):
        if self._debug:
            # TODO: logging.info() didn't work. Check logging levels?
            print(' | '.join([str(field) for field in fields]))


def relative_path(file):
    # https://stackoverflow.com/questions/4060221 for more options
    return os.path.join(os.path.dirname(__file__), file)

def to_data_uri(s, mime):
    uri = (
        ('data:' + mime + ';base64,').encode('utf8') +
        urlsafe_b64encode(s.encode('utf8'))
    ).decode("utf-8", "strict")
    return uri
