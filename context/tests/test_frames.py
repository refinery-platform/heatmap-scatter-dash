import unittest

import numpy as np
import pandas


from io import StringIO

from app.utils.frames import merge, reindex


class TestDataFrames(unittest.TestCase):

    def assertEqualDataFrames(self, a, b):
        a_np = np.array(a.as_matrix().tolist())
        b_np = np.array(b.as_matrix().tolist())
        np.testing.assert_equal(a_np, b_np)
        self.assertEqual(a.columns.tolist(),     b.columns.tolist())
        self.assertEqual(a.index.tolist(),       b.index.tolist())


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


class TestReindex(TestDataFrames):

    def setUp(self):
        csv = StringIO(
            '\n'.join([
                'a,b,hidden-id,c,d',
                'multiple,matches,X,Y,here',
                'multiple,matches,Z,W,maybe']))
        self.dataframe = pandas.read_csv(csv)

    # TODO: Separate class
    def test_reindex_good(self):
        indexed_df = reindex(self.dataframe, keys=['X', 'Y', 'Z'])
        target = pandas.DataFrame([
            ['multiple', 'matches', 'Y', 'here'],
            ['multiple', 'matches', 'W', 'maybe']],
            columns=['a', 'b', 'c', 'd'],
            index=['X', 'Z']
        )
        self.assertEqualDataFrames(target, indexed_df)

    def test_reindex_multiple(self):
        with self.assertRaisesRegex(
                Exception,
                r"Could not find a row where exactly one column matched keys: "
                "\['W', 'X', 'Y', 'Z'\]"):
            reindex(self.dataframe, keys=['W', 'X', 'Y', 'Z'])

    def test_reindex_none(self):
        with self.assertRaisesRegex(
                Exception,
                "None of the values \['multiple' 'matches' 'X' 'Y' 'here'\] "
                "in row 0 were recognized keys: "
                "\['something', 'entirely', 'different'\]"):
            reindex(self.dataframe, keys=[
                    'something', 'entirely', 'different'])
