import unittest

from app.utils.search import Index


class TestSearch(unittest.TestCase):
    def test_search(self):
        index = Index()
        index.add('foo')
        index.add('bar')
        index.add('foobar')
        self.assertEqual(set(index.search('ba')), {'bar', 'foobar'})
