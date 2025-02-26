import unittest

import numpy as np
import xarray as xr

from xcube.api.compute import compute_dataset

nan = float('nan')


class ComputeDatasetTest(unittest.TestCase):
    @classmethod
    def get_test_dataset(cls):
        return xr.Dataset(dict(a=(('y', 'x'), [[0.1, 0.2, 0.4, 0.1], [0.5, 0.1, 0.2, 0.3]]),
                               b=(('y', 'x'), [[0.4, 0.3, 0.2, 0.4], [0.1, 0.2, 0.5, 0.1]],
                                  dict(valid_pixel_expression='a >= 0.2')),
                               c=((), 1.0),
                               d=((), 1.0, dict(expression='a * b'))),
                          coords=dict(x=(('x',), [1, 2, 3, 4]), y=(('y',), [1, 2])),
                          attrs=dict(title='test_compute_dataset'))

    def test_compute_dataset_without_processed_variables(self):
        dataset = self.get_test_dataset()
        computed_dataset = compute_dataset(dataset)
        self.assertIsNot(computed_dataset, dataset)
        self.assertIn('x', computed_dataset)
        self.assertIn('y', computed_dataset)
        self.assertIn('a', computed_dataset)
        self.assertIn('b', computed_dataset)
        self.assertIn('c', computed_dataset)
        self.assertIn('d', computed_dataset)
        self.assertIn('x', computed_dataset.coords)
        self.assertIn('y', computed_dataset.coords)
        self.assertIn('title', computed_dataset.attrs)
        self.assertEqual((2, 4), computed_dataset.a.shape)
        self.assertEqual((2, 4), computed_dataset.b.shape)
        self.assertEqual((), computed_dataset.c.shape)
        self.assertNotIn('expression', computed_dataset.c.attrs)
        self.assertEqual((2, 4), computed_dataset.d.shape)
        self.assertIn('expression', computed_dataset.d.attrs)
        np.testing.assert_array_almost_equal(computed_dataset.a.values,
                                             np.array([[0.1, 0.2, 0.4, 0.1], [0.5, 0.1, 0.2, 0.3]]))
        np.testing.assert_array_almost_equal(computed_dataset.b.values,
                                             np.array([[nan, 0.3, 0.2, nan], [0.1, nan, 0.5, 0.1]]))
        np.testing.assert_array_almost_equal(computed_dataset.c.values,
                                             np.array([1.]))
        np.testing.assert_array_almost_equal(computed_dataset.d.values,
                                             np.array([[0.04, 0.06, 0.08, 0.04],
                                                       [0.05, 0.02, 0.1, 0.03]]))

    def test_compute_dataset_with_processed_variables(self):
        dataset = self.get_test_dataset()
        computed_dataset = compute_dataset(dataset,
                                           processed_variables=[('a', None),
                                                                ('b', dict(valid_pixel_expression=None)),
                                                                ('c', dict(expression='a + b')),
                                                                ('d', dict(valid_pixel_expression='c > 0.4'))])
        self.assertIsNot(computed_dataset, dataset)
        self.assertIn('x', computed_dataset)
        self.assertIn('y', computed_dataset)
        self.assertIn('a', computed_dataset)
        self.assertIn('b', computed_dataset)
        self.assertIn('c', computed_dataset)
        self.assertIn('d', computed_dataset)
        self.assertIn('x', computed_dataset.coords)
        self.assertIn('y', computed_dataset.coords)
        self.assertIn('title', computed_dataset.attrs)
        self.assertEqual((2, 4), computed_dataset.a.shape)
        self.assertEqual((2, 4), computed_dataset.b.shape)
        self.assertEqual((2, 4), computed_dataset.c.shape)
        self.assertIn('expression', computed_dataset.c.attrs)
        self.assertEqual((2, 4), computed_dataset.d.shape)
        self.assertIn('expression', computed_dataset.d.attrs)
        np.testing.assert_array_almost_equal(computed_dataset.a.values,
                                             np.array([[0.1, 0.2, 0.4, 0.1], [0.5, 0.1, 0.2, 0.3]]))
        np.testing.assert_array_almost_equal(computed_dataset.b.values,
                                             np.array([[0.4, 0.3, 0.2, 0.4], [0.1, 0.2, 0.5, 0.1]]))
        np.testing.assert_array_almost_equal(computed_dataset.c.values,
                                             np.array([[0.5, 0.5, 0.6, 0.5], [0.6, 0.3, 0.7, 0.4]]))
        np.testing.assert_array_almost_equal(computed_dataset.d.values,
                                             np.array([[0.04, 0.06, 0.08, 0.04], [0.05, nan, 0.1, nan]]))
