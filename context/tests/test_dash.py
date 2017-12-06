import unittest
from io import StringIO

import pandas

from app.app_wrapper import AppWrapper


class TestDash(unittest.TestCase):

    def setUp(self):
        csv = StringIO("""gene,cond1,cond2,cond3,cond4
            gene-one,0.2,0.7,0.2,0.7
            gene-two,0.4,0.8,0.2,0.8
            gene-three,0.5,0.8,0.1,0.9
            gene-four,0.6,0.8,0.3,0.8
            gene-five,0.6,0.9,0.4,0.8
            gene-six,0.6,0.9,0.5,0.8
            """)
        dataframe = pandas.read_csv(csv, index_col=0)
        self.app = AppWrapper(dataframe).app

    def test_layout(self):
        def tree(node):
            if hasattr(node, 'children'):
                return [tree(child) for child in node.children]
            else:
                return type(node).__name__
        scatter = ['Graph', ['Dropdown'], ['Dropdown']]
        scatter_search = ['Graph', ['Input'], ['Dropdown'], ['Dropdown']]
        self.assertEqual(
            tree(self.app.layout),
            [
                [
                    'Graph',
                    scatter],
                [
                    scatter_search,
                    scatter]]
        )

    def test_callback_map(self):
        self.assertEqual(
            list(self.app.callback_map.keys()),
            ['heatmap.figure']
            + ['scatter-%s.figure' % s for s in ['pca', 'genes', 'volcano']]
        )

    # Outside resource tests:

    def test_css(self):
        self.assertEqual(
            [css['namespace'] for css in self.app.css.get_all_css()],
            ['dash_core_components']
        )

    def test_scripts(self):
        self.assertEqual(
            [script['namespace'] for script
             in self.app.scripts.get_all_scripts()],
            ['dash_html_components',
             'dash_core_components',
             'dash_core_components']
        )

    # Config tests: unlike to change?

    def test_config(self):
        self.assertEqual(
            self.app.config,
            {
                'suppress_callback_exceptions': False,
                'routes_pathname_prefix': '/',
                'requests_pathname_prefix': '/'
            }
        )

    def test_registered_paths(self):
        self.assertEqual(
            self.app.registered_paths,
            {}
        )

    def test_routes(self):
        self.assertEqual(
            self.app.routes,
            []
        )

    def test_url_base(self):
        self.assertEqual(
            self.app.url_base_pathname,
            '/'
        )
