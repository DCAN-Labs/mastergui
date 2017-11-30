import unittest
from models import *


class TestCiftiSet(unittest.TestCase):
    def test_loads_list(self):
        p = "tests/ones.dscalar.nii"
        list = [p, p]
        cset = ciftiset.CiftiSet(list)
        cset.load_all()

        col1 = cset.getVectorPosition(0)

        self.assertEqual(len(col1), len(list))


if __name__ == '__main__':
    unittest.main()
