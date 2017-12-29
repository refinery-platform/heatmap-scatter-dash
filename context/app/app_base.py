import dash
import pandas
from plotly.figure_factory.utils import PLOTLY_SCALES

from app.utils.pca import pca


class AppBase:

    def __init__(self, dataframe,
                 diff_dataframes={'none given': pandas.DataFrame()},
                 colors='Greys',
                 reverse_colors=False,
                 heatmap_type='svg',
                 api_prefix=None):
        self._dataframe = dataframe
        self._dataframe_pca = pca(self._dataframe)
        self._diff_dataframes = diff_dataframes
        self._conditions = self._dataframe.axes[1].tolist()
        self._genes = self._dataframe.axes[0].tolist()
        if reverse_colors:
            self._color_scale = list(reversed(PLOTLY_SCALES[colors]))
        else:
            self._color_scale = PLOTLY_SCALES[colors]
        self._heatmap_type = heatmap_type
        self._css_urls = [
            'https://maxcdn.bootstrapcdn.com/'
            'bootstrap/3.3.7/css/bootstrap.min.css'
        ]
        self.app = dash.Dash()
        if api_prefix:
            self.app.config.update({
                'requests_pathname_prefix': api_prefix
            })
        self.app.title = 'Heatmap + Scatterplots'
        # Works, but not officially supported:
        # https://community.plot.ly/t/including-page-titles-favicon-etc-in-dash-app/4648
