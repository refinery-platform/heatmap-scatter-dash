import unittest

from app.utils.search import SimpleIndex, WhooshIndex


class TestIndex():
    def setUp(self):
        self.index = self.index_class()
        self.index.add('foo')
        self.index.add('bar', 'foobar', 'baz')
        # Should accept varargs

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

    def test_single_char_search(self):
        self.assertEqual(set(self.index.search('z')),
                         {'baz'})


class TestSimpleIndex(TestIndex, unittest.TestCase):
    def __init__(self, x):
        super().__init__(x)
        self.index_class = SimpleIndex


class TestWhooshIndex(TestIndex, unittest.TestCase):
    def __init__(self, x):
        super().__init__(x)
        self.index_class = WhooshIndex
