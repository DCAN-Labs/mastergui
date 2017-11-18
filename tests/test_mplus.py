import unittest
from models.mplus_model import *


class TestMPlusAnalyzer(unittest.TestCase):
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_results_parsing(self):
        m = MplusModel()
        look_for_fields = ['Akaike (AIC)', "CFI "]
        r = m.parse_mplus_results("output/DefaultTitle2017_11_17_16_54_46_882585voxel0.inp.out", look_for_fields)
        print(r)

if __name__ == '__main__':
    unittest.main()
