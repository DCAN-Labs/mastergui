import unittest

from models import *


class TestConfig(unittest.TestCase):
    def test_loadsfile(self):
        # d = os.path.dirname(__file__)
        # p = os.path.join(d,"config_file_for_testing.yml")
        p = "tests/config_file_for_testing.yml"
        c = config.Config(p)
        print(c._data)
        self.assertEqual(len(c._data), 1)
        self.assertEqual(len(c._data['animals']), 2)

    def test_handlemissingfile(self):
        with self.assertRaises(FileNotFoundError):
            p = "badpathnonexistentfile.txt"
            c = config.Config(p)


if __name__ == '__main__':
    unittest.main()
