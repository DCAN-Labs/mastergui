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
        self.additional_rule_save_data = {}

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
        self.template_MODEL_section = mplus_data.get("MODEL", "")

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
        """
        This iterates through the major sections of the original MPLUS templates and substitutes in any key values
        that have been set

        :return: return a string that is the full contents of an MPLUS model file, ready for execution by MPLUS
        """
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

    def add_rule(self, fields_from, operator, fields_to):
        new_rule_text = "%s %s %s;" % (",".join(fields_from), operator, ",".join(fields_to))
        self.rules.append(new_rule_text)
        self.mplus_data["MODEL"] = self.template_MODEL_section + "\n" + self.rules_to_s() + "\n"
        # self.mplus_data["MODEL:"] = self.rules_to_s()
        self.using_variables = set(self.using_variables.union(set(fields_from + fields_to)))

        for colname in (fields_from + fields_to):
            if colname not in self.voxelized_column_names_in_order:
                self.add_input_column_name(colname)
            else:
                print("was already in voxelized columns")

        # save the actual parameters for reuse after reloading from saved file
        self.additional_rule_save_data[new_rule_text] = [fields_from, operator, fields_to]

    def remove_rule_by_string(self, rule_as_string):
        if rule_as_string in self.rules:
            self.rules.remove(rule_as_string)
            self.mplus_data["MODEL"] = self.rules_to_s()
            # todo there may be less using variables now, check carefully and remove the necessary ones
        if rule_as_string in self.additional_rule_save_data:
            del self.additional_rule_save_data[rule_as_string]

    def rules_to_s(self):
        return "\n".join(self.rules)

    def save_for_datafile(self, datafile_path, mplus_input_file_path):
        self.datafile = datafile_path
        with open(mplus_input_file_path, "w", encoding='ascii') as f:
            output_string = self.to_string()
            f.write(output_string)
