import unittest

from app.app_wrapper import _log_interpolate


class TestColors(unittest.TestCase):

    def test_log_interpolate(self):
        linear = ['rgb(0,0,0)', 'rgb(255,255,255)']
        self.assertEqual(
            _log_interpolate(linear),
            [
                # This is a hack to make Plotly happy.
                [0, 'rgb(0.0, 0.0, 0.0)'],
                [0.0001, 'rgb(0.0, 0.0, 0.0)'],
                [0.001, 'rgb(63.75, 63.75, 63.75)'],
                [0.01, 'rgb(127.5, 127.5, 127.5)'],
                [0.1, 'rgb(191.25, 191.25, 191.25)'],
                [1, 'rgb(255.0, 255.0, 255.0)']]
        )
