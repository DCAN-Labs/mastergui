import unittest
from models.mplus_model import *
import os
import sys
from models import *
import glob


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
        test_output = "tests/mplus_output_sample.inp.out"
        r = m.parse_mplus_results(test_output, look_for_fields)
        print(r)
        print(type(r))

    def test_generate_inputs_from_voxels(self):
        print("todo")

    def test_process_voxel_based_outputs(self):
        print("todo")

    def test_run_whole_process(self):
        rootdir = os.getcwd()
        # todo we ultimately want a different config file for tests than for the main app
        config_path = os.path.join(rootdir, "config.yml")
        cfg = config.Config(config_path)
        analysis = mplus_analysis.MplusAnalysis(cfg)

        missing_tokens_list = ['', '-888', 'na']
        title = "unittests"
        model_path = "tests/mplus_input_sample.inp"
        model = mplus_model.MplusModel(model_path)
        model.add_rule(['COVA_AGE'], "on", ['COVA_IQ'])

        input_path = "tests/input_csv_file_test_case_Evan_simple.xlsx"

        input = input_spreadsheet.InputSpreadsheet(input_path)

        cap_at_n_vector_positions = 3
        print("begin_analysis test go")
        analysis.go(model, title, input, missing_tokens_list, testing_only_limit_to_n_rows=cap_at_n_vector_positions,
                    needsCiftiProcessing=True)
        print("done analysis test")
        # def go(self, model, title, input, missing_tokens_list, testing_only_limit_to_n_rows=3, needsCiftiProcessing=True):
        n_output_files = len(glob.glob(os.path.join(analysis.batchOutputDir, "*.inp.out")))
        self.assertEquals(n_output_files, cap_at_n_vector_positions)


if __name__ == '__main__':
    unittest.main()
