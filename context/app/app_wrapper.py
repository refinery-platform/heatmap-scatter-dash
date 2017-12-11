import dash
from plotly.figure_factory.utils import (PLOTLY_SCALES, label_rgb, n_colors,
                                         unlabel_rgb)

from app.cluster import cluster
from app.pca import pca
from app.app_layout import configure_layout
from app.app_callbacks import configure_callbacks


def _log_interpolate(color_scale):
    if len(color_scale) > 2:
        raise Exception('Expected just two points on color scale')
    points = 5  # TODO: We actually need to log the smallest value.
    interpolated = n_colors(
        unlabel_rgb(color_scale[1]),
        unlabel_rgb(color_scale[0]),
        points)
    missing_zero = [
        [10 ** -i, label_rgb(interpolated[i])]
        for i in reversed(range(points))
    ]
    # Without a point at zero, Plotly gives a color scale
    # that is mostly greys. No idea why.
    return [[0, label_rgb(interpolated[points - 1])]] + missing_zero



class AppWrapper:

    def __init__(self, dataframe, clustering=False, colors='Greys'):
        self._dataframe = cluster(dataframe) if clustering else dataframe
        self._dataframe_pca = pca(dataframe)
        self._conditions = self._dataframe.axes[1].tolist()
        self._color_scale = _log_interpolate(PLOTLY_SCALES[colors])
        self.app = dash.Dash()
        configure_layout(self)
        configure_callbacks(self)
