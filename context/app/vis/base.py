import dash
import pandas
from plotly.figure_factory.utils import PLOTLY_SCALES

from app.utils.pca import pca
from app.utils.search import SimpleIndex


class VisBase():

    def __init__(self,
                 union_dataframe,
                 diff_dataframes={'none given': pandas.DataFrame()},
                 colors='Greys',
                 reverse_colors=False,
                 most_variable_rows=500,
                 cluster_rows=False,
                 cluster_cols=False,
                 api_prefix=None,
                 debug=False,
                 server=None,
                 url_base_pathname=None):
        self._most_variable_rows = most_variable_rows
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
        self._debug = debug
        self.app = dash.Dash(server=server,
                             url_base_pathname=url_base_pathname)
        if api_prefix:
            self.app.config.update({
                'requests_pathname_prefix': api_prefix
            })
        self.app.title = 'Heatmap + Scatterplots'
        # Works, but not officially supported:
        # https://community.plot.ly/t/including-page-titles-favicon-etc-in-dash-app/4648

    # TODO: Remove?
    # def info(self, *fields):
    #     if self._debug:
    #         # TODO: logging.info() didn't work. Check logging levels?
    #         print(' | '.join([str(field) for field in fields]))
