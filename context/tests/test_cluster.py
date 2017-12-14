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

    def test_pass_through(self):
        clustered = cluster(
            self.dataframe, skip_zero=False,
            cluster_rows=False, cluster_cols=False, )
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

    def test_no_skip_cluster_both(self):
        clustered = cluster(
            self.dataframe, skip_zero=False,
            cluster_rows=True, cluster_cols=True)
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

    def test_skip_zero_cluster_both(self):
        clustered = cluster(
            self.dataframe, skip_zero=True,
            cluster_rows=True, cluster_cols=True)
        self.assertEqual(clustered.as_matrix().tolist(), [
            [0, 0, 4, 5],
            [1, 1, 4, 5],
            [8, 8, 4, 5],
            [9, 9, 4, 5]
        ])
        self.assertEqual(clustered.columns.tolist(), ['c1', 'c3', 'c2', 'c4'])
        self.assertEqual(clustered.index.tolist(), ['r1', 'r4', 'r3', 'r6'])

    def test_skip_zero_cluster_rows(self):
        clustered = cluster(self.dataframe, cluster_rows=True, skip_zero=True)
        self.assertEqual(clustered.as_matrix().tolist(), [
            [0, 4, 0, 5],
            [1, 4, 1, 5],
            [8, 4, 8, 5],
            [9, 4, 9, 5]
        ])
        self.assertEqual(clustered.columns.tolist(), ['c1', 'c2', 'c3', 'c4'])
        self.assertEqual(clustered.index.tolist(), ['r1', 'r4', 'r3', 'r6'])

    def test_skip_zero_cluster_cols(self):
        clustered = cluster(self.dataframe, cluster_cols=True, skip_zero=True)
        self.assertEqual(clustered.as_matrix().tolist(), [
            [0, 0, 4, 5],
            [8, 8, 4, 5],
            [1, 1, 4, 5],
            [9, 9, 4, 5]
        ])
        self.assertEqual(clustered.columns.tolist(), ['c1', 'c3', 'c2', 'c4'])
        self.assertEqual(clustered.index.tolist(), ['r1', 'r3', 'r4', 'r6'])
