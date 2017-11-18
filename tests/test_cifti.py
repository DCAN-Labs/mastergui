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
        m  = c.matrix()
        m[0, 0] = 1
        m[0, 1] = 2
        m[0, 3] = 3

        c.save("tests/mynewcifti.nii")


class TestCiftiSet(unittest.TestCase):
    def test_loads_list(self):
        p = "tests/ones.dscalar.nii"
        list = [p,p]
        cset = ciftiset.CiftiSet(list)
        cset.load_all()
        self.assertEqual(len(cset.ciftiMatrices),len(list))

        col1 = cset.getVectorPosition(0)
        print(col1)
        self.assertEqual(len(col1),2)

if __name__ == '__main__':
    unittest.main()
