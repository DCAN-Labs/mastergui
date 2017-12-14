import nipy
import nibabel
import unittest

from models import *


class TestInputSpreadsheet(unittest.TestCase):
    def test_preparewithcifti(self):
        input_path = "tests/input_csv_file_test_case_Evan_simple.xlsx"

#        def prepare_with_cifti(self, path_to_voxel_mappings, output_path_prefix, testing_only_limit_to_n_voxels=0,
#                               standard_missing_char=".", only_save_columns=[]):
        s = input_spreadsheet.InputSpreadsheet(input_path)

        mappings = [('PATH_HCP','VOXEL'), ('PATH_HCP2','VOXEL2')]

        s.prepare_with_cifti(mappings,"tests/output/test_preparewithcifti", testing_only_limit_to_n_voxels=3)



if __name__ == '__main__':
    unittest.main()
