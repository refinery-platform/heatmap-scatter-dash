import unittest

from app.app_callbacks import _select


class TestCallbacks(unittest.TestCase):

    def test_select_genes(self):
        points = [
            {'pointNumber': 0, 'x': 19, 'y': 17, 'text': 'ENSMUSG001'},
            {'pointNumber': 1, 'x': 28, 'y': 22, 'text': 'ENSMUSG002'}
        ]
        target = [
            'ENSMUSG001',
            'ENSMUSG002'
        ]
        search_term = None
        selected = _select(points, target, search_term)
        self.assertEqual(selected, ['ENSMUSG001', 'ENSMUSG002'])

    def test_select_conditions(self):
        points = [
            {'pointNumber': 0, 'x': -3, 'y': -2, 'text': 'kmc05'},
            {'pointNumber': 1, 'x': -2, 'y': 4, 'text': 'kmc07'}]
        target = ['kmc05', 'kmc07']
        search_term = None
        selected = _select(points, target, search_term)
        self.assertEqual(selected, ['kmc05', 'kmc07'])
