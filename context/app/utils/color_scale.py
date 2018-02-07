import re
from math import log2

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

    def _log_interpolations(self, min_val, max_val):
        points_per_pair = max(
            # Orders of magnitude spanned,
            # divided into intervals corresponding to successive rgb pairs.
            int(
                (log2(max_val) - log2(min_val))
                / (len(self._rgb_list) - 1)),
            # The max might not be double the min,
            # but we still want at least two points.
            1
        ) + 1
        return [
            n_colors(
                unlabel_rgb(self._rgb_list[i]),
                unlabel_rgb(self._rgb_list[i + 1]),
                points_per_pair)
            for i in range(len(self._rgb_list) - 1)
        ]

    def log(self, min_val, max_val):
        interpolations = self._log_interpolations(min_val, max_val)
        # Remove the first element from all, and concat
        trimmed = [i[1:] for i in interpolations]
        interpolation = sum(trimmed, [interpolations[0][0]])
        all_except_zero = [
            [2 ** -i, label_rgb(rgb)]
            for (i, rgb) in reversed(list(enumerate(reversed(interpolation))))
            # Two reverses, so the RGBs come out in the right order,
            # but the indices decrease, so 2 ** -i increases.
        ]
        # Without a point at zero, Plotly gives a color scale
        # that is mostly greys. No idea why.
        return [[0, label_rgb(interpolation[0])]] + all_except_zero

    def linear(self):
        return [[i / (len(self._rgb_list) - 1), color]
                for (i, color) in enumerate(self._rgb_list)]


palettes = {
    'greys': _ColorScale('#000000', '#FFFFFF'),
    'blue-white-red': _ColorScale('#0000FF', '#FFFFFF', '#FF0000'),
    'blue-black-red': _ColorScale('#0000FF', '#000000', '#FF0000'),
    'blue-yellow': _ColorScale('#0000FF', '#FFFF00'),
    'red-yellow': _ColorScale('#FF0000', '#FFFF00')
}