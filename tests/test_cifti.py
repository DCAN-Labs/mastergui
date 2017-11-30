import nipy
import nibabel
import unittest

from models import *


class TestCifti(unittest.TestCase):
    def test_loadsfile(self):
        # d = os.path.dirname(__file__)
        # p = os.path.join(d,"config_file_for_testing.yml")
        p = "tests/ones.dscalar.nii"
        c = cifti.Cifti(p)

        self.assertEqual(c.matrix.shape, (1, 91282))
        m = c.matrix
        m[0, 0] = 1
        m[0, 1] = 2
        m[0, 3] = 3

        c.save("tests/mynewcifti.nii")

    def test_ciftivalues(self):
        # todo
        p = "data/hcp_comm_det_damien/cub-sub-NDARINV02EBX0JJ_FNL_preproc_v2_Atlas_SMOOTHED_1.7.dtseries.nii_10_minutes_of_data_at_FD_0.2.dconn.nii_to_Merged_HCP_best80_dtseries.conc_AVG.dconn.dscalar.nii"
        # c = cifti.Cifti(p)

        # self.assertEqual(c.getPosition(18077), 0.735247)

    def test_writecifti(self):
        p = "tests/ones.dscalar.nii"
        p2 = "tests/onesMODIFIED.dscalar.nii"
        c = cifti.Cifti(p)
        c.setPosition(1, 2)
        self.assertEqual(c.getPosition(1), 2)
        c.save(p2)

        c2 = cifti.Cifti(p2)

        # self.assertEqual(c2.getPosition(0), 1)
        # self.assertEqual(c2.getPosition(2), 1)
        self.assertEqual(c2.getPosition(1), 2)


if __name__ == '__main__':
    unittest.main()
