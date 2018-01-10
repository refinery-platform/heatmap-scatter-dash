import unittest

from app.utils.search import Index


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.index = Index()
        self.index.add('foo')
        self.index.add('bar')
        self.index.add('foobar')

    def test_substring_search(self):
        self.assertEqual(set(self.index.search('ba')),
                         {'bar', 'foobar'})

    def test_none_search(self):
        self.assertEqual(set(self.index.search(None)),
                         {'foo', 'bar', 'foobar'})

    def test_empty_search(self):
        self.assertEqual(set(self.index.search('')),
                         {'foo', 'bar', 'foobar'})
