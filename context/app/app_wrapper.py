import dash
from plotly.figure_factory.utils import PLOTLY_SCALES

from app.utils.cluster import cluster
from app.utils.merge import merge
from app.utils.pca import pca


class AppWrapper:

    def __init__(self, dataframes=[],
                 cluster_rows=False, cluster_cols=False,
                 colors='Greys', heatmap_type='svg',
                 skip_zero=False):
        self._dataframe = cluster(
            merge(dataframes), skip_zero=skip_zero,
            cluster_rows=cluster_rows, cluster_cols=cluster_cols)
        self._dataframe_pca = pca(self._dataframe)
        self._conditions = self._dataframe.axes[1].tolist()
        self._genes = self._dataframe.axes[0].tolist()
        self._color_scale = PLOTLY_SCALES[colors]
        self._heatmap_type = heatmap_type
        self.css_urls = [
            'https://maxcdn.bootstrapcdn.com/'
            'bootstrap/3.3.7/css/bootstrap.min.css'
        ]
        self.app = dash.Dash()
        self.app.title = 'Heatmap + Scatterplots'
        # Works, but not officially supported:
        # https://community.plot.ly/t/including-page-titles-favicon-etc-in-dash-app/4648
