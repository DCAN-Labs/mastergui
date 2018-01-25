import re
from models import cifti
from models import ciftiset
import numpy as np
import pandas as pd
import logging


class MplusModel():
    """
    This class aids in reading and writing MPlus model files.
    There are some very important things to know about MPlus model files:
    (These are notes on some key points, not a general introduction to the MPlus Model file format.

    See their documentation for that.

    For example, http://global.oup.com/us/companion.websites/9780195367621/pdf/MplusQuickGuide2015.pdf
    )

    1) Mplus only reads the first 8 letters in variables names

    2) It expects the input data to NOT have column names but requires that all column names are provided in the NAMES section of the model.
        It is critical that the programmer always keep this in mind: the column order of any generated files must match the column order
        Provided in the NAMES section !!!

    3) Any variable used in the model must be listed in the USE VARIABLES section, even if it is already listed in the NAMES section

    4) beware of the unicode byte order mark U+FEFF creeping into the beginning of your generated text file, MPlus will give an error:
    " The input file does not contain valid commands:" in model files that appear to the eye to be just fine

    """

    def __init__(self, path=""):
        if len(path) > 0:
            self.load(path)
        self._title = "UntitledMplusModel"
        self.rules = []

        # track a unique list of variables used in the analysis
        self.using_variables = set([])
        self.input_column_names_in_order = []  # the order of this list MUST correspond to the order of columns in the input data files
        self.voxelized_column_names_in_order = []
        self.template_variable_values = {}

    def load(self, path):
        with open(path, 'r') as f:
            model_text = f.read()

        self.loadFromString(model_text)

    def loadFromString(self, model_text):
        self._raw = model_text
        self.parseMplus(model_text)

    def parseMplus(self, raw):

        p = re.compile('^[^\:\n]+\:', flags=re.MULTILINE)

        key_positions = [(m.start(0), m.end(0)) for m in re.finditer(p, raw)]

        mplus_data = {}
        key_order = []
        for i in range(len(key_positions)):
            k = key_positions[i]
            key = raw[k[0]:k[1]]
            if i < len(key_positions) - 1:
                value = raw[k[1]:key_positions[i + 1][0]]
            else:
                value = raw[k[1]:]
            if key[-1] == ":":
                key = key[:-1]

            mplus_data[key] = value
            key_order.append(key)
        self.key_order = key_order
        self.mplus_data = mplus_data

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title
        self.mplus_data["TITLE"] = title
        self.datafile = self.title_for_filename + ".csv"

    @property
    def title_for_filename(self):
        return re.sub('[^0-9a-zA-Z]+', '_', self.title)

    @property
    def datafile(self):
        return self._datafile

    @datafile.setter
    def datafile(self, datafile):
        self._datafile = datafile
        self.mplus_data["DATA"] = "FILE is %s;" % datafile

    @property
    def cluster(self):
        # todo still need logic for cluster
        return ""

    @property
    def cluster_clause(self):
        if len(self.cluster) == 0:
            return ""
        else:
            return "cluster=%s;\n" % self.cluster

    def add_using_variable(self, colname):
        if not colname in self.using_variables:
            self.using_variables = self.using_variables.union(set([colname]))

    def add_input_column_name(self, colname):
        if not colname in self.input_column_names_in_order:
            self.input_column_names_in_order.append(colname)

    def set_column_names(self, names):
        #        self.mplus_data["VARIABLE"] = (
        #        "Names are %s;\nUSEVARIABLES = %s;\n!auxiliary = #todo, \nMISSING=.;\ncluster= #todo" %
        #        ("\n\t".join(names), "\n\t".join(self.using_variables)))

        # assumes will be dropping all names but the column you are using.

        self.mplus_data["VARIABLE"] = ("Names are %s;\nUSEVARIABLES = %s;\nMISSING=.;\n%s" %
                                       ("\n\t".join(self.final_column_list()), "\n\t".join(self.using_variables),
                                        self.cluster_clause))

    def final_column_list(self):
        return self.input_column_names_in_order + self.voxelized_column_names_in_order

    def refresh_VARIABLE_section(self):

        # note this must include all columns in the GENERATED data, not the original non-imaging data
        # so it will be a combination of the columns from the original data source being used
        # and any generated columns of voxel data

        column_name_list = self.final_column_list()

        # order of the "using_variables" doesn't seem to be important at all for MPlus
        # but order of NAMES is CRITICAL (column names are not in the data source itself, their order is the only way that they are defined!)

        self.mplus_data["VARIABLE"] = ("Names are %s;\nUSEVARIABLES = %s;\nMISSING=.;\n%s" %
                                       (
                                           "\n\t".join(column_name_list), "\n\t".join(self.using_variables),
                                           self.cluster_clause))

    def apply_options(self, options_dict, non_original_data_columnlist):
        for k, v in options_dict.items():
            colname = v
            if colname not in non_original_data_columnlist:
                self.add_input_column_name(colname)

            if colname not in self.using_variables:
                self.add_using_variable(colname)

        self.set_column_names(self.input_column_names_in_order)

        self.template_variable_values = options_dict

        generated_mplus_model = self.to_string()

        # for k, v in options_dict.items():
        #    generated_mplus_model = generated_mplus_model.replace("{{%s}}" % k, str(v[0]))

        return generated_mplus_model

    def setTemplateVariableValues(self, options):
        self.template_variable_values = options

    def to_string(self):
        self.refresh_VARIABLE_section()

        output_str = ""
        for key in self.key_order:
            if len(output_str) > 0:
                output_str += "\n"
            output_str += key + ":\n"

            section_data = self.mplus_data[key]

            for k, v in self.template_variable_values.items():
                section_data = section_data.replace(self.template_text_for_variable(k), v)

            output_str += section_data

        if ord(output_str[0]) > 255:
            # for some reason a byte order mark character started showing up in the beginning of the generated
            # model file and mplus would choke on it
            output_str = output_str[1:]
        return output_str

    def template_text_for_variable(self, varname):
        return "{{%s}}" % varname

    def requires(self, include_already_set=False):
        """
        Returns a list of model parameters for which user input is required and how to attain them
        :param include_already_set:
        :return:
        """
        return ["Analysis", "Fields"]

    def getMappedName(self, from_col):
        return self.voxelizedMappings.get(from_col, from_col)

    def add_rule(self, fields_from, operator, fields_to):
        new_rule_text = "%s %s %s;" % (",".join(fields_from), operator, fields_to[0])
        self.rules.append(new_rule_text)
        self.mplus_data["MODEL"] = self.rules_to_s()
        # self.mplus_data["MODEL:"] = self.rules_to_s()
        self.using_variables = self.using_variables.union(set(fields_from + fields_to))

        for colname in (fields_from + fields_to):
            self.add_input_column_name(colname)

    def remove_rule_by_string(self, rule_as_string):
        if rule_as_string in self.rules:
            self.rules.remove(rule_as_string)
            self.mplus_data["MODEL"] = self.rules_to_s()
            # todo there may be less using variables now, check carefully and remove the necessary ones

    def rules_to_s(self):
        return "\n".join(self.rules)

    def aggregate_results(self, n_elements, path_template, look_for_fields, ciftis, naCiftiValue=-888,
                          testing_only_limit_to_n_rows=0):
        """
        parse results out of the per-voxel output files and aggregate them into cifti files. it accepts a list
        of fields to extract from the outputs and there must be one Cifti instance provided per field as
        we only write one given output field to one cifti at present
        :param inputspreadsheet:
        :param path_template:
        :param look_for_fields:
        :param ciftis:
        :return: a pandas data frame with the extracted values from the mplus output files
        """

        if len(look_for_fields) != len(ciftis):
            raise ValueError("Number of fields does not match number of ciftis")

        all_found_results = np.zeros((n_elements, len(look_for_fields)), dtype=np.float32)
        all_found_results[:] = np.nan

        for i in range(n_elements):
            path = path_template % str(i)  # + ".voxel" + str(i) + ".inp.out"
            results = self.parse_mplus_results(path, look_for_fields)
            for j in range(len(look_for_fields)):
                # todo how to handle NA's if field not found in results?
                fld = look_for_fields[j]
                value = results.get(fld, naCiftiValue)
                all_found_results[i, j] = value
                ciftis[j].setPosition(i, value)
            if testing_only_limit_to_n_rows > 0 and i >= testing_only_limit_to_n_rows - 1:
                print("stopping result aggregation early, testing mode")
                break

        all_results_df = pd.DataFrame(all_found_results, columns=look_for_fields)

        return all_results_df

    def aggregate_results_by_line_number(self, n_elements, path_template, line_matching_info):
        """
        parse results out of the per-voxel output files and aggregate them into cifti files. it accepts a list
        of fields to extract from the outputs and there must be one Cifti instance provided per field as
        we only write one given output field to one cifti at present
        :param inputspreadsheet:
        :param path_template:
        :param look_for_fields:
        :param ciftis:
        :return: a pandas data frame with the extracted values from the mplus output files
        """

        all_found_results = np.zeros((n_elements, len(line_matching_info)), dtype=np.float32)
        all_found_results[:] = np.nan

        for i in range(n_elements):
            path = path_template % str(i)  # + ".voxel" + str(i) + ".inp.out"
            results = self.extract_mplus_output_by_line_number(path, line_matching_info)
            for j in range(len(line_matching_info)):
                name = line_matching_info[j][2]
                # todo how to handle NA's if field not found in results?
                value = results[name]
                all_found_results[i, j] = value

        column_names = [m[2] for m in line_matching_info]
        all_results_df = pd.DataFrame(all_found_results, columns=column_names)

        return all_results_df

    def parse_mplus_results(self, path, look_for_fields=[]):

        seeking = len(look_for_fields)
        found = 0
        values = {}
        with open(path, "r") as f:
            lines = f.readlines()

            for l in lines:
                l = l.strip()
                for field in look_for_fields:
                    if l.find(field) == 0:
                        parts = l.split(" ")
                        value = parts[-1]
                        found += 1
                        values[field] = value
                        if found == seeking:
                            break
                if found == seeking:
                    break

        return values

    def extract_mplus_output_by_line_number(self, path, line_matching_info):
        """
        line_matching_info: tuple of form (line_number, sample_line, output name)
        """
        seeking = len(line_matching_info)
        found = 0
        values = {}
        with open(path, "r") as f:
            lines = f.readlines()

        for match in line_matching_info:
            line_number = match[0]
            sample_line = match[1]
            output_name = match[2]

            found = False
            tries = 0
            while tries < 5:

                line = lines[line_number]
                line_split = line.strip().split(" ")
                sample_split = sample_line.strip().split(" ")

                if line_split[0] == sample_split[0]:

                    last_value_in_line = line_split[-1]
                    try:
                        value = float(last_value_in_line)
                    except:
                        value = -999
                        err_msg = "Error extracting number for line %d of %s. Expected: \n%s, found: \n%s" % (
                        line_number, path, sample_line, line)
                        logging.error(err_msg)

                        # raise ValueError(err_msg)

                    values[output_name] = value
                    found = True
                    break
                else:
                    line_number += 1
                    tries += 1
            if not found:
                err_msg = "Mplus Output File Line %d in file %s in unexpected shape. Expected: \n%s, found: \n%s" % (
                line_number, path, sample_line, line)
                logging.error(err_msg)
                values[output_name] = -888
                # raise ValueError(err_msg)

        return values

    def save_for_datafile(self, datafile_path, mplus_input_file_path):
        self.datafile = datafile_path
        with open(mplus_input_file_path, "w", encoding='ascii') as f:
            output_string = self.to_string()
            f.write(output_string)
