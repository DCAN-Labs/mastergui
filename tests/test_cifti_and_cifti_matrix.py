import nipy
import nibabel
import unittest
import pandas as pd
import numpy as np

from models import *


class TestCiftiAndCiftiMatrix(unittest.TestCase):
    def test_loadsfile(self):
        # d = os.path.dirname(__file__)
        # p = os.path.join(d,"config_file_for_testing.yml")
        p = "tests/ones.dscalar.nii"
        c = cifti.Cifti(p)

        connectome_workbench_prefix = "/Applications/connectomeworkbench/bin_macosx64/"

        cm = cifti_matrix.CiftiMatrix(p,connectome_workbench_prefix)

        self.assertEqual(c.matrix.shape, (1, 91282))

        self.assertEqual(c.matrix.size, cm.matrix.size)
