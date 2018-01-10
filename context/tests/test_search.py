import unittest

from app.utils.search import Index


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.index = Index()
        self.index.add('foo')
        self.index.add('bar')
        self.index.add('foobar')
        self.index.add('baz')

    def test_unique_search(self):
        self.assertEqual(set(self.index.search('baz')),
                         {'baz'})

    def test_exact_search(self):
        self.assertEqual(set(self.index.search('bar')),
                         {'bar', 'foobar'})

    def test_substring_search(self):
        self.assertEqual(set(self.index.search('ba')),
                         {'bar', 'foobar', 'baz'})

    def test_multiple_search(self):
        self.assertEqual(set(self.index.search('oo az')),
                         {'foo', 'foobar', 'baz'})

    def test_none_search(self):
        self.assertEqual(set(self.index.search(None)),
                         {'foo', 'bar', 'foobar', 'baz'})

    def test_empty_search(self):
        self.assertEqual(set(self.index.search('')),
                         {'foo', 'bar', 'foobar', 'baz'})
