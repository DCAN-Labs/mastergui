import nipy
import nibabel
import unittest

from models import *


class TestMplusModel(unittest.TestCase):
    def test_reprocessdata(self):
        # d = os.path.dirname(__file__)
        # p = os.path.join(d,"config_file_for_testing.yml")
        p = "tests/ones.dscalar.nii"
        c = cifti.Cifti(p)
        c2 = cifti.Cifti(p)
        m = mplus_model.MplusModel()
        n = len(c.vector)

        path_template_for_data_including_voxel = "tests/output/input.voxel%s.inp.out"

        aggregated_results = m.aggregate_results(20, path_template_for_data_including_voxel,["Akaike (AIC)","Bayesian (BIC)"],[c,c2])

        print("survived")
        print(aggregated_results)

if __name__ == '__main__':
    unittest.main()
