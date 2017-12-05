import unittest
from math import copysign

import pandas

from app.pca import pca


class TestPCA(unittest.TestCase):

    def test_pca(self):
        def same_sign(a, b):
            return copysign(1, a) == copysign(1, b)

        dataframe = pandas.DataFrame(
            [[1, 2, 8, 9],
             [1, 2, 8, 9],
             [1, 2, 8, 9],
             [9, 1, 9, 1]],
            columns=['c1', 'c2', 'c3', 'c4'],
            index=['r1', 'r2', 'r3', 'r4']
        )
        principle_components = pca(dataframe)
        pca_list = principle_components.as_matrix().tolist()
        round_abs_pca_list =\
            principle_components.round().abs().as_matrix().tolist()
        self.assertEqual(round_abs_pca_list,
                         [[7.0, 3.0, 0.0, 0.0],
                          [5.0, 5.0, 0.0, 0.0],
                          [5.0, 5.0, 0.0, 0.0],
                          [7.0, 3.0, 0.0, 0.0]])
        self.assertTrue(same_sign(pca_list[0][0], pca_list[1][0]))
        self.assertTrue(same_sign(pca_list[0][1], pca_list[2][1]))
        # The pairs 0+1 and 2+3 are similar in the first component.
        # But 0+2 and 1+3 are also related, as shown in the second component.
        self.assertEqual(principle_components.columns.tolist(),
                         ['pc0', 'pc1', 'pc2', 'pc3'])
        self.assertEqual(principle_components.index.tolist(),
                         ['c1', 'c2', 'c3', 'c4'])
