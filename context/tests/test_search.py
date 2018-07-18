import unittest

from app.utils.search import SimpleIndex  # , WhooshIndex


class TestIndex():
    def setUp(self):
        self.index = self.index_class()
        self.index.add_document('fo', 'foo')
        self.index.add_document('br', 'bar')
        self.index.add_document('fb', 'foobar')
        self.index.add_document('bz', 'baz')
        # Should accept varargs

    def test_unique_search(self):
        self.assertEqual(set(self.index.search('baz')),
                         {'bz'})

    def test_exact_search(self):
        self.assertEqual(set(self.index.search('bar')),
                         {'br', 'fb'})

    def test_substring_search(self):
        self.assertEqual(set(self.index.search('ba')),
                         {'br', 'fb', 'bz'})

    def test_multiple_search(self):
        self.assertEqual(set(self.index.search('oo az')),
                         {'fo', 'fb', 'bz'})

    def test_padded_multiple_search(self):
        self.assertEqual(set(self.index.search('  oo  az  ')),
                         {'fo', 'fb', 'bz'})

    def test_none_search(self):
        self.assertEqual(set(self.index.search(None)),
                         {'fo', 'br', 'fb', 'bz'})

    def test_empty_search(self):
        self.assertEqual(set(self.index.search('')),
                         {'fo', 'br', 'fb', 'bz'})

    def test_single_char_search(self):
        self.assertEqual(set(self.index.search('z')),
                         {'bz'})


class TestSimpleIndex(TestIndex, unittest.TestCase):
    def __init__(self, x):
        super().__init__(x)
        self.index_class = SimpleIndex


# class TestWhooshIndex(TestIndex, unittest.TestCase):
#     def __init__(self, x):
#         super().__init__(x)
#         self.index_class = WhooshIndex
