import unittest

from app_runner import main
from app_runner_refinery import DefaultArgs


class TestAppRunner(unittest.TestCase):

    # from collections import namedtuple
    # def fake_args(self, args):
    #     return namedtuple('Args', args.keys())(**args)

    def test_html_error_false(self):
        args = DefaultArgs()
        with self.assertRaisesRegex(
                AttributeError,
                r"'DefaultArgs' object has no attribute 'port'"
        ):
            main(args)
