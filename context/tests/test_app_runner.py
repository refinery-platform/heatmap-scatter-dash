import unittest
from unittest.mock import patch

from dash import Dash
from flask import Flask

import app_runner


class TestAppRunner(unittest.TestCase):

    def full_args(self):
        return app_runner.arg_parser().parse_args(['--demo', '10', '10'])

    @patch.object(Flask, 'run')
    def test_default_args(self, mock_flask):
        args = self.full_args()
        app_runner.main(args)
        mock_flask.assert_called_once()


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
            app_runner.main(args)
        mock_dash.assert_not_called()
        mock_flask.assert_not_called()

    @patch.object(Flask, 'run')
    @patch.object(Dash, 'run_server')
    def test_bad_config_html_error_true(self, mock_dash, mock_flask):
        # Config has error, and the flask error server starts.
        args = self.full_args()
        args.html_error = True
        args.demo = None  # anything for a bad config
        app_runner.main(args)
        mock_dash.assert_not_called()
        mock_flask.assert_called_once()

    @patch.object(Flask, 'run')
    @patch.object(Dash, 'run_server')
    def test_good_config_html_error_false(self, mock_dash, mock_flask):
        # No error, and dash starts.
        args = self.full_args()
        args.html_error = False
        app_runner.main(args)
        mock_flask.assert_called_once()
        mock_dash.assert_not_called()

    @patch.object(Flask, 'run')
    @patch.object(Dash, 'run_server')
    def test_good_config_html_error_true(self, mock_dash, mock_flask):
        # No error, and dash starts. (html_error=True won't matter here.)
        args = self.full_args()
        args.html_error = True
        app_runner.main(args)
        mock_flask.assert_called_once()
        mock_dash.assert_not_called()
