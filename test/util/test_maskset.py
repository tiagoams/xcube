import unittest

import numpy as np
import xarray as xr
from numpy.testing import assert_array_almost_equal

from test.sampledata import create_highroc_dataset, create_c2rcc_flag_var, create_cmems_sst_flag_var
from xcube.util.maskset import MaskSet


class MaskSetTest(unittest.TestCase):
    def test_mask_set_with_flag_mask_str(self):
        flag_var = create_cmems_sst_flag_var()
        mask_set = MaskSet(flag_var)

        self.assertEqual('mask(sea=(1, None), land=(2, None), lake=(4, None), ice=(8, None))',
                         str(mask_set))

        mask_f1 = mask_set.sea
        self.assertIs(mask_f1, mask_set.sea)
        mask_f2 = mask_set.land
        self.assertIs(mask_f2, mask_set.land)
        mask_f3 = mask_set.lake
        self.assertIs(mask_f3, mask_set.lake)
        mask_f4 = mask_set.ice
        self.assertIs(mask_f4, mask_set.ice)

        validation_data = ((0, 'sea', mask_f1, np.array([[[1, 0, 0, 0],
                                                          [1, 1, 0, 0],
                                                          [1, 1, 1, 0]]],
                                                        dtype=np.uint8)),
                           (1, 'land', mask_f2, np.array([[[0, 1, 0, 0],
                                                           [0, 0, 1, 1],
                                                           [0, 0, 0, 1]]],
                                                         dtype=np.uint8)),
                           (2, 'lake', mask_f3, np.array([[[0, 0, 1, 1],
                                                           [0, 0, 0, 0],
                                                           [0, 0, 0, 0]]],
                                                         dtype=np.uint8)),
                           (3, 'ice', mask_f4, np.array([[[1, 1, 1, 0],
                                                          [1, 0, 0, 0],
                                                          [0, 0, 0, 0]]],
                                                        dtype=np.uint8)))

        for index, name, mask, data in validation_data:
            self.assertIs(mask, mask_set[index])
            self.assertIs(mask, mask_set[name])
            assert_array_almost_equal(mask.values, data, err_msg=f'{index}, {name}, {mask.name}')

    def test_mask_set_with_flag_mask_int_array(self):
        flag_var = create_c2rcc_flag_var()
        mask_set = MaskSet(flag_var)

        self.assertEqual('c2rcc_flags(F1=(1, None), F2=(2, None), F3=(4, None), F4=(8, None))',
                         str(mask_set))

        mask_f1 = mask_set.F1
        self.assertIs(mask_f1, mask_set.F1)
        mask_f2 = mask_set.F2
        self.assertIs(mask_f2, mask_set.F2)
        mask_f3 = mask_set.F3
        self.assertIs(mask_f3, mask_set.F3)
        mask_f4 = mask_set.F4
        self.assertIs(mask_f4, mask_set.F4)

        validation_data = ((0, 'F1', mask_f1, np.array([[1, 1, 1, 1],
                                                        [1, 0, 1, 0],
                                                        [0, 1, 1, 1]],
                                                       dtype=np.uint8)),
                           (1, 'F2', mask_f2, np.array([[0, 0, 0, 0],
                                                        [0, 0, 0, 1],
                                                        [0, 0, 0, 0]],
                                                       dtype=np.uint8)),
                           (2, 'F3', mask_f3, np.array([[0, 0, 0, 0],
                                                        [0, 1, 0, 0],
                                                        [0, 0, 0, 0]],
                                                       dtype=np.uint8)),
                           (3, 'F4', mask_f4, np.array([[0, 0, 0, 0],
                                                        [0, 0, 0, 0],
                                                        [1, 0, 0, 0]],
                                                       dtype=np.uint8)))

        for index, name, mask, data in validation_data:
            self.assertIs(mask, mask_set[index])
            self.assertIs(mask, mask_set[name])
            assert_array_almost_equal(mask.values, data)

    def test_get_mask_sets(self):
        dataset = create_highroc_dataset()
        mask_sets = MaskSet.get_mask_sets(dataset)
        self.assertIsNotNone(mask_sets)
        self.assertEqual(len(mask_sets), 1)
        self.assertIn('c2rcc_flags', mask_sets)
        mask_set = mask_sets['c2rcc_flags']
        self.assertIsInstance(mask_set, MaskSet)

    def test_mask_set_with_flag_values(self):
        s2l2a_slc_meanings = ['no_data',
                              'saturated_or_defective',
                              'dark_area_pixels',
                              'cloud_shadows',
                              'vegetation',
                              'bare_soils',
                              'water',
                              'clouds_low_probability_or_unclassified',
                              'clouds_medium_probability',
                              'clouds_high_probability',
                              'cirrus',
                              'snow_or_ice']

        data = np.array([[1, 2, 8, 3],
                         [7, 6, 0, 4],
                         [9, 5, 11, 10]], dtype=np.uint8)
        flag_var = xr.DataArray(data,
                                dims=('y', 'x'),
                                name='SLC',
                                attrs=dict(
                                    long_name="Scene classification flags",
                                    flag_values=','.join(f'{i}' for i in range(len(s2l2a_slc_meanings))),
                                    flag_meanings=' '.join(s2l2a_slc_meanings),
                                ))

        mask_set = MaskSet(flag_var)

        self.assertEqual('SLC(no_data=(None, 0), saturated_or_defective=(None, 1), dark_area_pixels=(None, 2), '
                         'cloud_shadows=(None, 3), vegetation=(None, 4), bare_soils=(None, 5), water=(None, 6), '
                         'clouds_low_probability_or_unclassified=(None, 7), clouds_medium_probability=(None, 8), '
                         'clouds_high_probability=(None, 9), cirrus=(None, 10), snow_or_ice=(None, 11))',
                         str(mask_set))

        validation_data = ((0, 'no_data', mask_set.no_data, np.array([[0, 0, 0, 0],
                                                                      [0, 0, 1, 0],
                                                                      [0, 0, 0, 0]],
                                                                     dtype=np.uint8)),
                           (4, 'vegetation', mask_set.vegetation, np.array([[0, 0, 0, 0],
                                                                            [0, 0, 0, 1],
                                                                            [0, 0, 0, 0]],
                                                                           dtype=np.uint8)),
                           (10, 'cirrus', mask_set.cirrus, np.array([[0, 0, 0, 0],
                                                                     [0, 0, 0, 0],
                                                                     [0, 0, 0, 1]],
                                                                    dtype=np.uint8)),
                           (6, 'water', mask_set.water, np.array([[0, 0, 0, 0],
                                                                  [0, 1, 0, 0],
                                                                  [0, 0, 0, 0]],
                                                                 dtype=np.uint8)))

        for index, name, mask, data in validation_data:
            msg = f'index={index}, name={name!r}, data={data!r}'
            self.assertIs(mask, mask_set[index], msg=msg)
            self.assertIs(mask, mask_set[name], msg=msg)
            assert_array_almost_equal(mask.values, data, err_msg=msg)

        self.assertEqual(set(s2l2a_slc_meanings), set(dir(mask_set)))

        html = mask_set._repr_html_()
        self.assertTrue(html.startswith('<html>'))
        self.assertTrue(html.endswith('</html>'))
