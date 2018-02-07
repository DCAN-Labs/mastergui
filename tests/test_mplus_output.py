
import unittest

from models.mplus.output_parser import *

class TestMplusModelOutput(unittest.TestCase):
    def test_reprocessdata(self):
        print("begin test_reprocessdata")
        # d = os.path.dirname(__file__)
        # p = os.path.join(d,"config_file_for_testing.yml")
        p = "tests/data/sample.input.voxel0.inp.out"

        o = MplusOutput(p)


        #o.print_report()

        #print(o.warnings)
        print("end test_reprocessdata")

    def test_dir_of_output(self):
        print("begin test_dir_of_output")
        pattern = "tests/data/sample.input.voxel%d.inp.out"
        pattern = "../masterguioutput/fullsetofvoxels/input.voxel%d.inp.out"

        output_set = MplusOutputSet(pattern)

        #stats = output_set.extract(["STANDARDIZED MODEL RESULTS|Means|PC6|Estimate"],2)
        stats = output_set.extract(["MODEL FIT INFORMATION|Information Criteria|Bayesian (BIC)"])
        print(stats)
        print("WARNINGS:")
        print(output_set.warning_counts)

        print("NOT FOUND Counts")
        print(output_set.not_found_counts)
        print("end test_dir_of_output")


if __name__ == '__main__':
    unittest.main()
