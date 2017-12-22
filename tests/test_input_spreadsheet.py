import os
import nipy
import nibabel
import unittest
import pandas as pd
import time

from models import *


class TestInputSpreadsheet(unittest.TestCase):
    def test_preparewithcifti(self):
        input_path = "tests/input_csv_file_test_case_Evan_simple.xlsx"

#        def prepare_with_cifti(self, path_to_voxel_mappings, output_path_prefix, testing_only_limit_to_n_voxels=0,
#                               standard_missing_char=".", only_save_columns=[]):
        s = input_spreadsheet.InputSpreadsheet(input_path)

        mappings = [('PATH_HCP','VOXEL'), ('PATH_HCP2','VOXEL2')]

        output_prefix = "tests/output/test_preparewithcifti"

        limit_to_voxel_count = 200
        begin_time = time.time()

        s.prepare_with_cifti(mappings,output_prefix, testing_only_limit_to_n_voxels=limit_to_voxel_count)

        end_time = time.time()
        print("Elapsed time for the generation of the voxelized files %s" % (end_time - begin_time))
        source_data = s._data

        for voxel_idx in range(limit_to_voxel_count):

            result = pd.read_csv("%s.%d.csv" % (output_prefix, voxel_idx), header=None)

            for row_idx in range(source_data.shape[0]):

                for mapping in mappings:

                    idx_of_mapped_column = source_data.columns.get_loc(mapping[0])

                    src_value = source_data.iloc[row_idx, idx_of_mapped_column]

                    self.assertTrue(os.path.exists(src_value), "Check that cifti path is valid")

                    voxelized_value = result.iloc[row_idx,idx_of_mapped_column]

                    actual_number_count = 0

                    #test that the value is either numeric or ".", the canonical representation of missing data.
                    try:
                        as_num = float(voxelized_value)
                        actual_number_count += 1
                    except:
                        self.assertTrue(voxelized_value == ".", "Non-numeric and not '.' value found")
                    #confirm the row actually had a valid path
        self.assertTrue(actual_number_count>0, "Checking that any values were numeric in the voxelized columns")

if __name__ == '__main__':
    unittest.main()
