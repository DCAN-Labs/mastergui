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

        mappings = [('PATH_HCP', 'VOXEL'), ('PATH_HCP2', 'VOXEL2')]

        output_prefix = "tests/output/test_preparewithcifti"

        limit_to_voxel_count = 200
        begin_time = time.time()

        columns_to_use = ["COVA_AGE", "COVA_SEX"]
        s.prepare_with_cifti(mappings, output_prefix,
                             testing_only_limit_to_n_voxels=limit_to_voxel_count,
                             only_save_columns=columns_to_use)

        end_time = time.time()
        print("Elapsed time for the generation of the voxelized files %s" % (end_time - begin_time))
        source_data = s._data

        for voxel_idx in range(limit_to_voxel_count):
            file_name = "%s.%d.csv" % (output_prefix, voxel_idx)
            print("Checking file %s" % file_name)
            result = pd.read_csv(file_name, header=None)

            for row_idx in range(source_data.shape[0]):

                for mapping_i in range(len(mappings)):
                    mapping = mappings[mapping_i]

                    idx_of_mapped_column = len(columns_to_use) + mapping_i

                    src_value = source_data.iloc[row_idx, idx_of_mapped_column]

                    self.assertTrue(os.path.exists(src_value), "Check that cifti path is valid")

                    print("about to check %d %d" % (row_idx, idx_of_mapped_column))
                    voxelized_value = result.iloc[row_idx, idx_of_mapped_column]

                    actual_number_count = 0

                    # test that the value is either numeric or ".", the canonical representation of missing data.
                    try:
                        as_num = float(voxelized_value)
                        actual_number_count += 1
                    except:
                        self.assertTrue(voxelized_value == ".", "Non-numeric and not '.' value found")
                        # confirm the row actually had a valid path
        self.assertTrue(actual_number_count > 0, "Checking that any values were numeric in the voxelized columns")


if __name__ == '__main__':
    unittest.main()
