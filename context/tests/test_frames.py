import tempfile
import unittest
from io import StringIO

import numpy as np
import pandas

from app.utils.frames import (center_and_scale_rows, find_index, merge,
                              sort_by_variance)
from app.utils.vulcanize import vulcanize
from app.utils import tabular
from app_runner import file_dataframes


class TestDataFrames(unittest.TestCase):

    def assertEqualDataFrames(self, a, b, message=''):
        self.assertEqual(a.shape, b.shape, message)
        a_np = np.array(a.as_matrix().tolist())
        b_np = np.array(b.as_matrix().tolist())
        np.testing.assert_equal(a_np, b_np, message)
        self.assertEqual(a.columns.tolist(), b.columns.tolist(), message)
        self.assertEqual(a.index.tolist(), b.index.tolist(), message)


class TestCenterAndScale(TestDataFrames):

    def test_center_and_scale(self):
        df = pandas.DataFrame([
            [1, 2, 3],
            [2, 4, 6]
        ])
        scaled_df = center_and_scale_rows(df)
        self.assertEqualDataFrames(
            pandas.DataFrame([
                [-1, 0, 1],
                [-1, 0, 1]
            ]),
            scaled_df
        )


class TestTabularParser(TestDataFrames):

    def setUp(self):
        self.target = pandas.DataFrame([
            [2, 3]],
            columns=['b', 'c'],
            index=[1]
        )

    def assert_file_read(self, input_bytes, target, kwargs={}, message=None):
        file = tempfile.NamedTemporaryFile(mode='wb+')
        file.write(input_bytes)
        file.seek(0)
        df = tabular.parse(file, **kwargs)
        self.assertEqualDataFrames(df, target, message)

    def test_read_crazy_delimiters(self):
        for c in '~!@#$%^&*|:;':
            self.assert_file_read(
                bytes('{0}b{0}c\n1{0}2{0}3'.format(c), 'utf-8'),
                self.target,
                message='Failed with {} as delimiter'.format(c)
            )

    # Easier just to make the data on the commandline
    # than to create it inside python:
    #   $ gzip fake.csv
    #   >>> open('fake.csv.gz', 'rb').read()

    def test_read_gzip(self):
        self.assert_file_read(
            b'\x1f\x8b\x08\x08\xe5\xf2\x82Z\x00\x03fake.csv\x00\xd3I\xd2I\xe62\xd41\xd21\x06\x00\xfb\x9a\xc9\xa6\n\x00\x00\x00', self.target)  # noqa: E501

    def test_read_zip(self):
        self.assert_file_read(
            b'PK\x03\x04\n\x00\x00\x00\x00\x00\x8dZML\xfb\x9a\xc9\xa6\n\x00\x00\x00\n\x00\x00\x00\x08\x00\x1c\x00fake.csvUT\t\x00\x03J\x10\x83Zk\x11\x83Zux\x0b\x00\x01\x04\xf6\x01\x00\x00\x04\x14\x00\x00\x00,b,c\n1,2,3PK\x01\x02\x1e\x03\n\x00\x00\x00\x00\x00\x8dZML\xfb\x9a\xc9\xa6\n\x00\x00\x00\n\x00\x00\x00\x08\x00\x18\x00\x00\x00\x00\x00\x01\x00\x00\x00\xa4\x81\x00\x00\x00\x00fake.csvUT\x05\x00\x03J\x10\x83Zux\x0b\x00\x01\x04\xf6\x01\x00\x00\x04\x14\x00\x00\x00PK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x00N\x00\x00\x00L\x00\x00\x00\x00\x00', self.target  # noqa: E501
        )

    def test_read_csv(self):
        self.assert_file_read(b',b,c\n1,2,3', self.target)

    def test_read_csv_remove_strings(self):
        self.assert_file_read(b',b,c,xxx\n1,2,3,X!', self.target)

    def test_read_csv_keep_strings(self):
        self.assert_file_read(
            b',b,c,xxx\n1,2,3,X!',
            pandas.DataFrame([
                [2, 3, 'X!']],
                columns=['b', 'c', 'xxx'],
                index=[1]
            ),
            kwargs={'keep_strings': True})

    def test_read_csv_rn(self):
        self.assert_file_read(b',b,c\r\n1,2,3', self.target)

    def test_read_csv_quoted(self):
        self.assert_file_read(b',"b","c"\n"1","2","3"', self.target)

    def test_read_tsv(self):
        self.assert_file_read(b'\tb\tc\n1\t2\t3', self.target)

    def test_read_gct(self):
        self.assert_file_read(
            b'#1.2\n1\t1\nNames\tDescription\tb\tc\n1\tfoo\t2\t3', self.target)


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
        by_variance = sort_by_variance(dataframe)
        self.assertEqualDataFrames(
            by_variance,
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
            columns=['xLOGx_NO', 'logFoldChange_NO', 'Log2-change_YES',
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
                columns=['Log2-change_YES', '-log10(p-value!)'],
                index=['gene1', 'gene2']
            )
        )
