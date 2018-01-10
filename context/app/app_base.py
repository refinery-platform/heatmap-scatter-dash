from base64 import urlsafe_b64encode

import dash
import pandas
from plotly.figure_factory.utils import PLOTLY_SCALES

from app.utils.pca import pca
from app.utils.search import Index


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
        self._genes_index = Index()
        for gene in self._genes:
            self._genes_index.add(gene)
        if reverse_colors:
            self._color_scale = list(reversed(PLOTLY_SCALES[colors]))
        else:
            self._color_scale = PLOTLY_SCALES[colors]
        self._heatmap_type = heatmap_type
        self._css_urls = [
            'https://maxcdn.bootstrapcdn.com/'
            'bootstrap/3.3.7/css/bootstrap.min.css',
            to_data_uri(
                """
                .plotlyjsicon {
                    display: none;
                }
                iframe {
                    border: none;
                    width: 100%;
                    height: 33vh;
                }
                table {
                    border: none;
                }
                td, th {
                    border: none;
                    padding: 0 5px;
                }
                """,
                "text/css")
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


def to_data_uri(s, mime):
    uri = (
        ('data:' + mime + ';base64,').encode('utf8') +
        urlsafe_b64encode(s.encode('utf8'))
    ).decode("utf-8", "strict")
    return uri
