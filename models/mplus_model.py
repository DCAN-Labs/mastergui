import re
from models import cifti
from models import ciftiset
import numpy as np
import pandas as pd
import logging


class MplusModel():
    def __init__(self, path=""):
        if len(path) > 0:
            self.load(path)
        self._title = "UntitledMplusModel"
        self.rules = []
        self.voxelizedMappings = {}

        # track a unique list of variables used in the analysis
        self.using_variables = set([])
        self.input_column_names_in_order = []  #the order of this list MUST correspond to the order of columns in the input data files


    def load(self, path):
        with open(path, 'r') as f:
            model_text = f.read()

        self.loadFromString(model_text)

    def loadFromString(self,model_text):
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
        #todo still need logic for cluster
        return ""

    @property
    def cluster_clause(self):
        if len(self.cluster) == 0:
            return ""
        else:
            return "cluster=%s;\n" % self.cluster

    def add_using_variable(self,colname):
        if not colname in self.using_variables:
            self.using_variables = self.using_variables.union(set([colname]))

    def add_input_column_name(self,colname):
        if not colname in self.input_column_names_in_order:
            self.input_column_names_in_order.append(colname)



    def set_column_names(self, names):
        #        self.mplus_data["VARIABLE"] = (
        #        "Names are %s;\nUSEVARIABLES = %s;\n!auxiliary = #todo, \nMISSING=.;\ncluster= #todo" %
        #        ("\n\t".join(names), "\n\t".join(self.using_variables)))

        #assumes will be dropping all names but the column you are using.

        keeping_column_names = [self.getMappedName(name) for name in names if self.getMappedName(name) in self.using_variables]
        self.mplus_data["VARIABLE"] = ("Names are %s;\nUSEVARIABLES = %s;\nMISSING=.;\n%s" %
                                       ("\n\t".join(self.input_column_names_in_order), "\n\t".join(self.using_variables), self.cluster_clause))

    def apply_options(self, options_dict):
        for k, v in options_dict.items():
            colname = v[0]  # todo this assumes only one element there
            self.add_input_column_name(colname)
            self.add_using_variable(colname)

        self.set_column_names(self.input_column_names_in_order)

        generated_mplus_model = self.to_string()

        for k, v in options_dict.items():
            generated_mplus_model = generated_mplus_model.replace("{{%s}}" % k, str(v[0]))

        return generated_mplus_model

    def to_string(self):
        output_str = ""
        for key in self.key_order:
            output_str += "\n" + key + ":\n"
            output_str += self.mplus_data[key]

        return output_str

    def requires(self, include_already_set=False):
        """
        Returns a list of model parameters for which user input is required and how to attain them
        :param include_already_set:
        :return:
        """
        return ["Analysis", "Fields"]

    def set_voxelized_mappings(self, mappings):
        for m in mappings:
            self.add_voxelized_colname_mapping(m[0],m[1])

    def add_voxelized_colname_mapping(self, from_col, new_name):
        self.voxelizedMappings[from_col] = new_name

    def getMappedName(self, from_col):
        return self.voxelizedMappings.get(from_col,from_col)

    def add_rule(self, fields_from, operator, fields_to):
        new_rule_text = "%s %s %s;" % (",".join(fields_from), operator, fields_to[0])
        self.rules.append(new_rule_text)
        self.mplus_data["MODEL"] = self.rules_to_s()
        # self.mplus_data["MODEL:"] = self.rules_to_s()
        self.using_variables = self.using_variables.union(set(fields_from + fields_to))

        for colname in (fields_from + fields_to):
            self.add_input_column_name(colname)

    def rules_to_s(self):
        return "\n".join(self.rules)

    def aggregate_results(self, n_elements, path_template, look_for_fields, ciftis, naCiftiValue=-888, testing_only_limit_to_n_rows = 0):
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
                all_found_results[i,j] = value
                ciftis[j].setPosition(i, value)
            if testing_only_limit_to_n_rows >0 and i >= testing_only_limit_to_n_rows - 1:
                print("stopping result aggregation early, testing mode")
                break

        all_results_df = pd.DataFrame(all_found_results, columns = look_for_fields)

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
                all_found_results[i,j] = value

        column_names = [m[2] for m in line_matching_info]
        all_results_df = pd.DataFrame(all_found_results, columns = column_names)

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
                        err_msg = "Error extracting number for line %d of %s. Expected: \n%s, found: \n%s" % (line_number, path, sample_line, line)
                        logging.error(err_msg)

                        #raise ValueError(err_msg)

                    values[output_name] =  value
                    found = True
                    break
                else:
                    line_number += 1
                    tries+=1
            if not found:
                err_msg = "Mplus Output File Line %d in file %s in unexpected shape. Expected: \n%s, found: \n%s" % (line_number, path, sample_line, line)
                logging.error(err_msg)
                values[output_name] = -888
                #raise ValueError(err_msg)

        return values