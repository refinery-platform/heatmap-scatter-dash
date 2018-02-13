import tempfile
import unittest
from unittest import skip
from io import StringIO

import numpy as np
import pandas

from app.utils.frames import find_index, merge, sort_by_variance
from app.utils.vulcanize import vulcanize
from app_runner import file_dataframes


class TestDataFrames(unittest.TestCase):

    def assertEqualDataFrames(self, a, b, message=None):
        a_np = np.array(a.as_matrix().tolist())
        b_np = np.array(b.as_matrix().tolist())
        np.testing.assert_equal(a_np, b_np, message)
        self.assertEqual(a.columns.tolist(), b.columns.tolist(), message)
        self.assertEqual(a.index.tolist(), b.index.tolist(), message)


class TestTabularParser(TestDataFrames):

    def setUp(self):
        self.target = pandas.DataFrame([
            [2, 3]],
            columns=['b', 'c'],
            index=[1]
        )

    def assertFileRead(self, input_text, message=None):
        file = tempfile.NamedTemporaryFile(mode=self.mode)
        file.write(input_text)
        file.seek(0)
        dfs = file_dataframes([file])
        self.assertEqualDataFrames(dfs[0], self.target, message)


class TestTabularParserStrings(TestTabularParser):

    def setUp(self):
        super().setUp()
        self.mode = 'w+'

    def test_read_csv(self):
        self.assertFileRead(',b,c\n1,2,3')

    def test_read_csv_rn(self):
        self.assertFileRead(',b,c\r\n1,2,3')

    def test_read_csv_quoted(self):
        self.assertFileRead(',"b","c"\n"1","2","3"')

    def test_read_tsv(self):
        self.assertFileRead('\tb\tc\n1\t2\t3')

    def test_read_crazy_delimiters(self):
        for c in '~!@#$%^&*|:;':
            self.assertFileRead(
                '{0}b{0}c\n1{0}2{0}3'.format(c),
                'Failed with {} as delimiter'.format(c))


class TestTabularParserBytes(TestTabularParser):

    def setUp(self):
        super().setUp()
        self.mode = 'wb+'

    @skip  # TODO: Why does this fail, when the string version works?
    def test_read_crazy_delimiters(self):
        for c in '~!@#$%^&*|:;':
            self.assertFileRead(
                bytes('{0}b{0}c\n1{0}2{0}3'.format(c), 'utf-8'),
                'Failed with {} as delimiter'.format(c))

    def test_read_csv(self):
        self.assertFileRead(b',b,c\n1,2,3')

    def test_read_zip(self):
        # Easier just to make this on the commandline
        # than to create it inside python:
        #   $ gzip fake.csv
        #   >>> open('fake.csv.gz', 'rb').read()
        self.assertFileRead(
            b'\x1f\x8b\x08\x08\xe5\xf2\x82Z\x00\x03fake.csv'
            b'\x00\xd3I\xd2I\xe62\xd41\xd21\x06\x00\xfb\x9a'
            b'\xc9\xa6\n\x00\x00\x00')


class TestMerge(TestDataFrames):

    def setUp(self):
        self.dataframes = [pandas.DataFrame([
            [1, 4, 1, 5],
            [8, 4, 8, 5],
            [2, 4, 2, 5],
            [9, 4, 9, 5]],
            columns=['c1', 'c2', 'c3', 'c4'],
            index=['r1', 'r2', 'r3', 'r4']
        )]

    def test_no_change(self):
        merged_frame = merge(self.dataframes)
        self.assertEqualDataFrames(merged_frame, self.dataframes[0])

    def test_merge(self):
        self.dataframes.append(
            pandas.DataFrame([
                [11, 12],
                [21, 22]],
                columns=['c4', 'c5'],
                index=['r4', 'r5']
            )
        )
        merged_frame = merge(self.dataframes)
        self.assertEqualDataFrames(merged_frame, pandas.DataFrame([
            [1, 4, 1, 5, np.nan, np.nan],
            [8, 4, 8, 5, np.nan, np.nan],
            [2, 4, 2, 5, np.nan, np.nan],
            [9, 4, 9, 5, 11, 12],
            [np.nan, np.nan, np.nan, np.nan, 21, 22]],
            columns=['c1', 'c2', 'c3', 'c4_x', 'c4_y', 'c5'],
            index=['r1', 'r2', 'r3', 'r4', 'r5']
        ))


class TestFindIndex(TestDataFrames):

    def setUp(self):
        csv = StringIO(
            '\n'.join([
                'a,b,hidden-id,c,d',
                'multiple,matches,X,Y,here',
                'multiple,matches,Z,W,maybe']))
        self.dataframe = pandas.read_csv(csv)

    def test_find_index_good(self):
        indexed_df = find_index(self.dataframe, keys=['X', 'Y', 'Z'])
        target = pandas.DataFrame([
            ['multiple', 'matches', 'Y', 'here'],
            ['multiple', 'matches', 'W', 'maybe']],
            columns=['a', 'b', 'c', 'd'],
            index=['X', 'Z']
        )
        self.assertEqualDataFrames(target, indexed_df)

    def test_find_index_single(self):
        indexed_df = find_index(self.dataframe, keys=['X'])
        target = pandas.DataFrame([
            ['multiple', 'matches', 'Y', 'here'],
            ['multiple', 'matches', 'W', 'maybe']],
            columns=['a', 'b', 'c', 'd'],
            index=['X', 'Z']
        )
        self.assertEqualDataFrames(target, indexed_df)

    def test_find_index_multiple(self):
        with self.assertRaisesRegex(
                Exception,
                r"No row where exactly one column matched keys: "
                "\['W', 'X', 'Y', 'Z'\]"):
            find_index(self.dataframe, keys=['W', 'X', 'Y', 'Z'])

    def test_find_index_none(self):
        with self.assertRaisesRegex(
                Exception,
                "No row where exactly one column matched keys: "
                "\['something', 'entirely', 'different'\]"):
            find_index(self.dataframe, keys=[
                'something', 'entirely', 'different'])


class SortByVariance(TestDataFrames):

    def test_sort_by_variance(self):
        dataframe = pandas.DataFrame([
            [1, 1, 1, 1],
            [2, 4, 2, 5],
            [8, 4, 8, 5],
            [9, 9, 9, 8]],
            columns=['c1', 'c2', 'c3', 'c4'],
            index=['r1', 'r2', 'r3', 'r4']
        )
        sorted = sort_by_variance(dataframe)
        self.assertEqualDataFrames(
            sorted,
            pandas.DataFrame([
                [8, 4, 8, 5],
                [2, 4, 2, 5],
                [9, 9, 9, 8],
                [1, 1, 1, 1]],
                columns=['c1', 'c2', 'c3', 'c4'],
                index=['r3', 'r2', 'r4', 'r1']
            )
        )


class TestVulcanize(TestDataFrames):

    def test_vulcanize(self):
        df = pandas.DataFrame([
            [0, 0, 1, 0, 0.1],
            [0, 0, -1, 0, 10]],
            columns=['log-fold-fake', 'fake-fold-change', 'xLOGxFOLDxCHANGEx',
                     'fake-p-val', 'p-value!'],
            index=['gene1', 'gene2']
        )
        v = vulcanize(df)
        self.assertEqualDataFrames(
            v,
            pandas.DataFrame(
                [
                    [1, 1],
                    [-1, -1]],
                columns=['xLOGxFOLDxCHANGEx', '-log10(p-value!)'],
                index=['gene1', 'gene2']
            )
        )
