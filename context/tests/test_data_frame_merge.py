import unittest
from io import StringIO


from app.data_frame_merge import DataFrameMerge
import pandas
import numpy as np

class TestDataFrameMerge(unittest.TestCase):

    def setUp(self):
        self.dataframes = [pandas.DataFrame([
                [1, 4, 1, 5],
                [8, 4, 8, 5],
                [2, 4, 2, 5],
                [9, 4, 9, 5]],
            columns=['c1', 'c2', 'c3', 'c4'],
            index=['r1', 'r2', 'r3', 'r4']
        )]

    def assertEqualDataFrames(self, a, b):
        a_np = np.array(a.as_matrix().tolist())
        b_np = np.array(b.as_matrix().tolist())
        np.testing.assert_equal(a_np, b_np)
        self.assertEqual(a.columns.tolist(),     b.columns.tolist())
        self.assertEqual(a.index.tolist(),       b.index.tolist())

    def test_no_change(self):
        merged_frame = DataFrameMerge(self.dataframes).count_frame
        self.assertEqualDataFrames(merged_frame, self.dataframes[0])

    def test_cluster(self):
        # Anything much more than this should be tested in test_cluster.py
        merged_frame = DataFrameMerge(self.dataframes, clustering=True).count_frame
        self.assertEqualDataFrames(merged_frame, pandas.DataFrame([
                [1, 1, 4, 5],
                [2, 2, 4, 5],
                [8, 8, 4, 5],
                [9, 9, 4, 5]],
            columns=['c1', 'c3', 'c2', 'c4'],
            index=['r1', 'r3', 'r2', 'r4']
        ))

    def test_merge(self):
        self.dataframes.append(
            pandas.DataFrame([
                    [11, 12],
                    [21, 22]],
                columns=['c4', 'c5'],
                index=['r4', 'r5']
            )
        )
        merged_frame = DataFrameMerge(self.dataframes).count_frame
        self.assertEqualDataFrames(merged_frame, pandas.DataFrame([
            [1, 4, 1, 5, np.nan, np.nan],
            [8, 4, 8, 5, np.nan, np.nan],
            [2, 4, 2, 5, np.nan, np.nan],
            [9, 4, 9, 5, 11, 12],
            [np.nan, np.nan, np.nan, np.nan, 21, 22]],
            columns=['c1', 'c2', 'c3', 'c4_x', 'c4_y', 'c5'],
            index=['r1', 'r2', 'r3', 'r4', 'r5']
        ))
