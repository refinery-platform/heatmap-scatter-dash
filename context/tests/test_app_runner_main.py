import unittest

from app_runner import main


from collections import namedtuple


class TestAppRunnerMain(unittest.TestCase):

    def parse_args(self, args):
        return namedtuple('Args', args.keys())(**args)

    def test_html_error_false(self):
        args = {
            'demo': True,
            'html_error': False
        }
        with self.assertRaisesRegex(
                AttributeError,
                # This will change as new params are introduced.
                r"'Args' object has no attribute 'files'"
        ):
            main(self.parse_args(args))
