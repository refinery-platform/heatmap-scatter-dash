import unittest

from app.utils.color_scale import _ColorScale


class TestColorScale(unittest.TestCase):

    def test_linear_two_points(self):
        scale = _ColorScale('#000000', '#FFFFFF')
        self.assertEqual(
            scale.linear(),
            [[0, 'rgb(0,0,0)'],
             [1, 'rgb(255,255,255)']])

    def test_linear_two_points_reversed(self):
        scale = _ColorScale('#000000', '#FFFFFF').reversed
        self.assertEqual(
            scale.linear(),
            [[0, 'rgb(255,255,255)'],
             [1, 'rgb(0,0,0)']])

    def test_linear_three_points(self):
        scale = _ColorScale('#0000FF', '#FFFFFF', '#FF0000')
        self.assertEqual(
            scale.linear(),
            [[0, 'rgb(0,0,255)'],
             [0.5, 'rgb(255,255,255)'],
             [1, 'rgb(255,0,0)']])

    def test_linear_three_points_reversed(self):
        scale = _ColorScale('#0000FF', '#FFFFFF', '#FF0000').reversed
        self.assertEqual(
            scale.linear(),
            [[0, 'rgb(255,0,0)'],
             [0.5, 'rgb(255,255,255)'],
             [1, 'rgb(0,0,255)']])

    def test_log_interpolations_two_points(self):
        scale = _ColorScale('#000000', '#FFFFFF')
        self.assertEqual(
            scale._log_interpolations(4, 64),
            [[(0.0, 0.0, 0.0),  # 4
              (63.75, 63.75, 63.75),  # 8
              (127.5, 127.5, 127.5),  # 16
              (191.25, 191.25, 191.25),  # 32
              (255.0, 255.0, 255.0)]])  # 64

    def test_log_interpolations_three_points(self):
        scale = _ColorScale('#0000FF', '#FFFFFF', '#FF0000')
        self.assertEqual(
            scale._log_interpolations(4, 8),
            [[(0.0, 0.0, 255.0), (255.0, 255.0, 255.0)],
             [(255.0, 255.0, 255.0), (255.0, 0.0, 0.0)]])

        self.assertEqual(
            scale._log_interpolations(4, 64),
            [[(0.0, 0.0, 255.0),
              (127.5, 127.5, 255.0),
              (255.0, 255.0, 255.0)],
             [(255.0, 255.0, 255.0),
              (255.0, 127.5, 127.5),
              (255.0, 0.0, 0.0)]])

    def test_log_two_points(self):
        scale = _ColorScale('#000000', '#FFFFFF')
        self.assertEqual(
            scale.log(4, 8),
            [[0, 'rgb(0.0, 0.0, 0.0)'],
             [0.5, 'rgb(0.0, 0.0, 0.0)'],
             [1, 'rgb(255.0, 255.0, 255.0)']])

        self.assertEqual(
            scale.log(4, 32),
            [[0, 'rgb(0.0, 0.0, 0.0)'],
             [0.125, 'rgb(0.0, 0.0, 0.0)'],
             [0.25, 'rgb(85.0, 85.0, 85.0)'],
             [0.5, 'rgb(170.0, 170.0, 170.0)'],
             [1, 'rgb(255.0, 255.0, 255.0)']])

    def test_log_three_points(self):
        scale = _ColorScale('#0000FF', '#FFFFFF', '#FF0000')
        self.assertEqual(
            scale.log(4, 8),
            [[0, 'rgb(0.0, 0.0, 255.0)'],
             [0.25, 'rgb(0.0, 0.0, 255.0)'],
             [0.5, 'rgb(255.0, 255.0, 255.0)'],
             [1, 'rgb(255.0, 0.0, 0.0)']])

        self.assertEqual(
            scale.log(4, 128),
            [[0, 'rgb(0.0, 0.0, 255.0)'],
             [0.0625, 'rgb(0.0, 0.0, 255.0)'],
             [0.125, 'rgb(127.5, 127.5, 255.0)'],
             [0.25, 'rgb(255.0, 255.0, 255.0)'],
             [0.5, 'rgb(255.0, 127.5, 127.5)'],
             [1, 'rgb(255.0, 0.0, 0.0)']])
