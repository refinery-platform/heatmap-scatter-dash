import unittest
from base64 import urlsafe_b64decode

from app.app_wrapper import _log_interpolate, _to_data_uri


class TestUtils(unittest.TestCase):

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

    def test_to_data_uri(self):
        orig = 'alert("testing 123?")'
        uri = _to_data_uri(orig)
        encoded = 'YWxlcnQoInRlc3RpbmcgMTIzPyIp'
        self.assertEqual(
            uri,
            'data:application/javascript;base64,' + encoded
        )
        self.assertEqual(
            b'alert("testing 123?")',
            urlsafe_b64decode(encoded)
        )
