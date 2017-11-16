import nipy
import nibabel



#
#
# paths = ["Conte69.MyelinAndCorrThickness.32k_fs_LR.dscalar.nii"	,
# "Conte69.parcellations_VGD11b.32k_fs_LR.dlabel.nii"	,
# "ones.dscalar.nii",
# "Conte69.MyelinAndCorrThickness.32k_fs_LR.dtseries.nii",
# "Conte69.MyelinAndCorrThickness.32k_fs_LR.ptseries.nii"]
#
#
#
#
# path = "Conte69.MyelinAndCorrThickness.32k_fs_LR.dscalar.nii"
#
# for path in paths:
#     d = nibabel.cifti2.cifti2.load(path)
#
#     m = d.get_fdata()
#
#     print(m.shape)


import unittest

from models import *


class TestCifti(unittest.TestCase):
    def test_loadsfile(self):
        # d = os.path.dirname(__file__)
        # p = os.path.join(d,"config_file_for_testing.yml")
        p = "tests/ones.dscalar.nii"
        c = cifti.Cifti(p)

        self.assertEqual(c.matrix().shape, (1,91282))


if __name__ == '__main__':
    unittest.main()
