import unittest
from app.app import app

def tree(node):
    if hasattr(node, 'children'):
        return [tree(child) for child in node.children]
    else:
        return type(node).__name__


class TestApp(unittest.TestCase):

    def test_layout(self):
        self.assertEqual(
            tree(app.layout),
            [
                ['Input', 'Dropdown', 'Dropdown'],
                'Graph', 'Graph'
            ]
        )

    def test_callback_map(self):
        self.assertEqual(
            list(app.callback_map.keys()),
            ['scatter.figure', 'heatmap.figure']
        )

    # Outside resource tests:

    def test_css(self):
        self.assertEqual(
            [css['namespace'] for css in app.css.get_all_css()],
            ['dash_core_components']
        )

    def test_scripts(self):
        self.assertEqual(
            [script['namespace'] for script in app.scripts.get_all_scripts()],
            ['dash_html_components', 'dash_core_components', 'dash_core_components']
        )

    # Config tests: unlike to change?

    def test_config(self):
        self.assertEqual(
            app.config,
            {
                'suppress_callback_exceptions': False,
                'routes_pathname_prefix': '/',
                'requests_pathname_prefix': '/'
            }
        )

    def test_registered_paths(self):
        self.assertEqual(
            app.registered_paths,
            {}
        )

    def test_routes(self):
        self.assertEqual(
            app.routes,
            []
        )

    def test_url_base(self):
        self.assertEqual(
            app.url_base_pathname,
           '/'
        )
