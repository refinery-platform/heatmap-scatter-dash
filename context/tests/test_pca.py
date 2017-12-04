import unittest

import pandas

from app.pca import pca


class TestPCA(unittest.TestCase):

    def test_pca(self):
        dataframe = pandas.DataFrame(
            [[1, 2, 8, 9],
             [1, 2, 8, 9],
             [1, 2, 8, 9],
             [9, 1, 9, 1]],
            columns=['c1', 'c2', 'c3', 'c4'],
            index=['r1', 'r2', 'r3', 'r4']
        )
        principle_components = pca(dataframe)
        self.assertEqual(principle_components.round().as_matrix().tolist(),
                         [[7.0, 3.0],
                          [5.0, -5.0],
                          [-5.0, 5.0],
                          [-7.0, -3.0]]
                         )
        # The pairs 1+2 and 3+4 are similar in the first component.
        # But 1+3 and 2+4 are also related, as shown in the second component.
        self.assertEqual(principle_components.columns.tolist(),
                         ['pc0', 'pc1']
                         )
        self.assertEqual(principle_components.index.tolist(),
                         ['c1', 'c2', 'c3', 'c4']
                         )
