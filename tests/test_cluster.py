import unittest

import pandas

from app.cluster import cluster


class TestCluster(unittest.TestCase):

    def test_cluster(self):
        dataframe = pandas.DataFrame(
            [
                [1, 4, 1, 5],
                [8, 4, 8, 5],
                [2, 4, 2, 5],
                [9, 4, 9, 5]
            ],
            columns=['c1', 'c2', 'c3', 'c4'],
            index=['r1', 'r2', 'r3', 'r4']
        )
        clustered = cluster(dataframe)
        self.assertEqual(clustered.as_matrix().tolist(), [
            [1, 1, 4, 5],
            [2, 2, 4, 5],
            [8, 8, 4, 5],
            [9, 9, 4, 5]
        ])
        self.assertEqual(clustered.columns.tolist(), ['c1', 'c3', 'c2', 'c4'])
        self.assertEqual(clustered.index.tolist(), ['r1', 'r3', 'r2', 'r4'])
