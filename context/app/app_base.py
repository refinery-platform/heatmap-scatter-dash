import dash
import pandas
from plotly.figure_factory.utils import PLOTLY_SCALES

from app.utils.pca import pca


class AppBase:

    def __init__(self, dataframe,
                 diff_dataframes={'none given': pandas.DataFrame()},
                 colors='Greys',
                 heatmap_type='svg'):
        self._dataframe = dataframe
        self._dataframe_pca = pca(self._dataframe)
        self._diff_dataframes = diff_dataframes
        self._conditions = self._dataframe.axes[1].tolist()
        self._genes = self._dataframe.axes[0].tolist()
        self._color_scale = PLOTLY_SCALES[colors]
        self._heatmap_type = heatmap_type
        self._css_urls = [
            'https://maxcdn.bootstrapcdn.com/'
            'bootstrap/3.3.7/css/bootstrap.min.css'
        ]
        self.app = dash.Dash(
            # This did not work:
            # url_base_pathname=''

            # TODO: Will this get it to make API requests to relative URLs?
            requests_pathname_prefix=''
            # https://community.plot.ly/t/deploy-dash-on-apache-server-solved/4855
        )
        self.app.title = 'Heatmap + Scatterplots'
        # Works, but not officially supported:
        # https://community.plot.ly/t/including-page-titles-favicon-etc-in-dash-app/4648
