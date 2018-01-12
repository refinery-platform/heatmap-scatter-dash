import unittest
from unittest.mock import patch

from dash import Dash
from flask import Flask

from app_runner import main
from app_runner_refinery import DefaultArgs


class TestAppRunner(unittest.TestCase):

    def full_args(self):
        args = DefaultArgs()
        args.port = 12345
        args.demo = [2, 2]
        args.files = []
        args.diffs = []
        args.api_prefix = None
        args.cluster_rows = False
        args.cluster_cols = False
        return args

    def test_default_args(self):
        args = DefaultArgs()
        with self.assertRaisesRegex(
                AttributeError,
                r"'DefaultArgs' object has no attribute 'port'"
        ):
            main(args)

    @patch.object(Flask, 'run')
    @patch.object(Dash, 'run_server')
    def test_bad_config_html_error_false(self, mock_dash, mock_flask):
        # Config has error, and it should not be caught.
        args = self.full_args()
        args.html_error = False
        args.demo = None  # anything for a bad config
        with self.assertRaisesRegex(
                Exception,
                r'Either "demo" or "files" is required'
        ):
            main(args)
        mock_dash.assert_not_called()
        mock_flask.assert_not_called()

    @patch.object(Flask, 'run')
    @patch.object(Dash, 'run_server')
    def test_bad_config_html_error_true(self, mock_dash, mock_flask):
        # Config has error, and the flask error server starts.
        args = self.full_args()
        args.html_error = True
        args.demo = None  # anything for a bad config
        main(args)
        mock_dash.assert_not_called()
        mock_flask.assert_called_once()

    @patch.object(Flask, 'run')
    @patch.object(Dash, 'run_server')
    def test_good_config_html_error_false(self, mock_dash, mock_flask):
        # No error, and dash starts.
        args = self.full_args()
        args.html_error = False
        main(args)
        mock_dash.assert_called_once()
        mock_flask.assert_not_called()

    @patch.object(Flask, 'run')
    @patch.object(Dash, 'run_server')
    def test_good_config_html_error_true(self, mock_dash, mock_flask):
        # No error, and dash starts. (html_error=True won't matter here.)
        args = self.full_args()
        args.html_error = True
        main(args)
        mock_dash.assert_called_once()
        mock_flask.assert_not_called()
