
import unittest

from models.mplus.output_parser import *

class TestMplusModelOutput(unittest.TestCase):
    def test_reprocessdata(self):


        # d = os.path.dirname(__file__)
        # p = os.path.join(d,"config_file_for_testing.yml")
        p = "tests/sample.mplus.modelwarning.out"

        o = MplusOutput(p)

        o.print_report()

if __name__ == '__main__':
    unittest.main()
