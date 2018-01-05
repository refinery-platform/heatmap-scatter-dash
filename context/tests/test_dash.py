import unittest

import pandas

from app.app_callbacks import AppCallbacks


class TestDash():

    # This test was useful at first, but I think it's too hard to maintain now.
    # def test_layout(self):
    #     def tree(node):
    #         if hasattr(node, 'children'):
    #             return [tree(child) for child in node.children]
    #         else:
    #             return type(node).__name__
    #     self.assertEqual(
    #         tree(self.app.layout),
    #         ['something...']
    #     )

    def test_callback_map(self):
        self.assertEqual(
            list(self.app.callback_map.keys()),
            ['heatmap.figure',
              'scatter-sample-by-sample.figure',
              'scatter-volcano.figure',
              'table-iframe.srcDoc',
              'list-iframe.srcDoc',
              'search-genes-timestamp.children',
              'scatter-sample-by-sample-timestamp.children',
              'scatter-volcano-timestamp.children',
              'search-genes-ids-json.children',
              'scatter-sample-by-sample-ids-json.children',
              'scatter-volcano-ids-json.children',
              'selected-genes-ids-json.children']
        )

    # Outside resource tests:

    def test_css(self):
        self.assertEqual(
            [(css['namespace'] if 'namespace' in css else None)
             for css
             in self.app.css.get_all_css()],
            ['dash_core_components',
             None,
             None]
        )

    def test_scripts(self):
        self.assertEqual(
            [(script['namespace'] if 'namespace' in script else None)
             for script
             in self.app.scripts.get_all_scripts()],
            ['dash_html_components',
             'dash_core_components',
             'dash_core_components',
             None,
             None,
             None]
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

    def counts_dataframe(self):
        return pandas.DataFrame([
            [1, 2],
            [3, 4]],
            columns=['c1', 'c2'],
            index=['r1', 'r2']
        )

    def diff_dataframe(self):
        return pandas.DataFrame([
            [1, 2],
            [3, 4]],
            columns=['log_fold_change', 'p_value'],
            index=['r1', 'r2']
        )


class TestDashNoDifferentials(TestDash, unittest.TestCase):

    def setUp(self):
        self.app = AppCallbacks(
            dataframe=self.counts_dataframe()
        ).app


class TestDashWithDifferentials(TestDash, unittest.TestCase):

    def setUp(self):
        self.app = AppCallbacks(
            dataframe=self.counts_dataframe(),
            diff_dataframes={
                'A': self.diff_dataframe(),
                'B': self.diff_dataframe(),
            }
        ).app
