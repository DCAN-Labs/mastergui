import unittest

from models import *


class TestConfig(unittest.TestCase):
    def test_loadsfile(self):
        p = "tests/data/config.test.json"
        c = config.Config(p)

        # not important what value we test for, just verifying that
        # some (any) key value lookup is succeeding in this test
        self.assertEqual(c['testvalue'], "justfortest")

    def test_handlemissingfile(self):
        with self.assertRaises(FileNotFoundError):
            p = "badpathnonexistentfile.txt"
            c = config.Config(p)


if __name__ == '__main__':
    unittest.main()
