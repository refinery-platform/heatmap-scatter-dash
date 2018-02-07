import re
from math import log10

from plotly.figure_factory.utils import label_rgb, n_colors, unlabel_rgb


def _hex_to_rgb(hex):
    assert re.fullmatch('#[0-9A-F]{6}', hex)
    rgb = [str(int(hex[i:i + 2], 16)) for i in (1, 3, 5)]
    return 'rgb({})'.format(','.join(rgb))


class _ColorScale():
    def __init__(self, *hex_list, reverse=True):
        self._rgb_list = [_hex_to_rgb(h) for h in hex_list]
        if reverse:
            self.reversed = _ColorScale(*reversed(hex_list), reverse=False)

    def log(self, min, max):
        points = int(log10(max) - log10(min)) + 2
        interpolated = n_colors(
            unlabel_rgb(self._rgb_list[1]),
            unlabel_rgb(self._rgb_list[0]),
            points)
        all_except_zero = [
            [10 ** -i, label_rgb(interpolated[i])]
            for i in reversed(range(points))
        ]
        # Without a point at zero, Plotly gives a color scale
        # that is mostly greys. No idea why.
        return [[0, label_rgb(interpolated[points - 1])]] + all_except_zero

    def linear(self):
        return [[i, color] for (i, color) in enumerate(self._rgb_list)]


palettes = {
    'greys': _ColorScale('#000000', '#FFFFFF')
}
