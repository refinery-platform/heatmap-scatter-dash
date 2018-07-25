import unittest

import pandas

from app.utils.cluster import cluster


class TestCluster(unittest.TestCase):

    def setUp(self):
        self.dataframe = pandas.DataFrame(
            [
                [0, 4, 0, 5],
                [0, 0, 0, 0],
                [8, 4, 8, 5],
                [1, 4, 1, 5],
                [0, 0, 0, 0],
                [9, 4, 9, 5]
            ],
            columns=['c1', 'c2', 'c3', 'c4'],
            index=['r1', 'r2', 'r3', 'r4', 'r5', 'r6']
        )

    def assert_no_change(self, array):
        dataframe = pandas.DataFrame(array)
        clustered = cluster(dataframe, cluster_rows=True, cluster_cols=True)
        self.assertEqual(clustered.as_matrix().tolist(), array)

    def test_1_1(self):
        self.assert_no_change([[1]])

    def test_1_2(self):
        self.assert_no_change([[1, 2]])

    def test_2_1(self):
        self.assert_no_change([[2, 1]])

    def test_2_2(self):
        self.assert_no_change([[1, 2], [3, 4]])

    def test_pass_through(self):
        clustered = cluster(self.dataframe)
        self.assertEqual(clustered.as_matrix().tolist(), [
            [0, 4, 0, 5],
            [0, 0, 0, 0],
            [8, 4, 8, 5],
            [1, 4, 1, 5],
            [0, 0, 0, 0],
            [9, 4, 9, 5]
        ])
        self.assertEqual(clustered.columns.tolist(), ['c1', 'c2', 'c3', 'c4'])
        self.assertEqual(clustered.index.tolist(), [
                         'r1', 'r2', 'r3', 'r4', 'r5', 'r6'])

    def test_cluster_both(self):
        clustered = cluster(
            self.dataframe, cluster_rows=True, cluster_cols=True)
        self.assertEqual(clustered.as_matrix().tolist(), [
            [8, 8, 4, 5],
            [9, 9, 4, 5],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 4, 5],
            [1, 1, 4, 5],
        ])
        self.assertEqual(clustered.columns.tolist(), ['c1', 'c3', 'c2', 'c4'])
        self.assertEqual(clustered.index.tolist(), [
                         'r3', 'r6', 'r2', 'r5', 'r1', 'r4'])
