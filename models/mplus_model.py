import re
from models import cifti
from models import ciftiset


class MplusModel():
    def __init__(self, path=""):
        if len(path) > 0:
            self.load(path)
        self._title = "UntitledMplusModel"
        self.rules = []

        # track a unique list of variables used in the analysis
        self.using_variables = set([])

    def load(self, path):
        with open(path, 'r') as f:
            self._raw = f.read()
        self.parseMplus(self._raw)

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
        return "COVA_SEX"

    @property
    def cluster_clause(self):
        if len(self.cluster) == 0:
            return ""
        else:
            return "cluster=%s;\n" % self.cluster

    def set_column_names(self, names):
        print(self.key_order)
        #        self.mplus_data["VARIABLE"] = (
        #        "Names are %s;\nUSEVARIABLES = %s;\n!auxiliary = #todo, \nMISSING=.;\ncluster= #todo" %
        #        ("\n\t".join(names), "\n\t".join(self.using_variables)))

        self.mplus_data["VARIABLE"] = ("Names are %s;\nUSEVARIABLES = %s;\nMISSING=.;\n%s" %
                                       ("\n\t".join(names), "\n\t".join(self.using_variables), self.cluster_clause))

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

    def add_rule(self, fields_from, operator, fields_to):
        new_rule_text = "%s %s %s;" % (",".join(fields_from), operator, fields_to[0])
        self.rules.append(new_rule_text)
        self.mplus_data["MODEL"] = self.rules_to_s()
        # self.mplus_data["MODEL:"] = self.rules_to_s()
        self.using_variables = self.using_variables.union(set(fields_from + fields_to))

    def rules_to_s(self):
        return "\n".join(self.rules)

    def aggregate_results_to_cifti(self, inputspreadsheet, path_prefix, look_for_fields, ciftis, naCiftiValue=-888):
        """
        parse results out of the per-voxel output files and aggregate them into cifti files. it accepts a list
        of fields to extract from the outputs and there must be one Cifti instance provided per field as
        we only write one given output field to one cifti at present
        :param inputspreadsheet:
        :param path_prefix:
        :param look_for_fields:
        :param ciftis:
        :return:
        """

        max_todo = 3
        if len(look_for_fields) != len(ciftis):
            raise ValueError("Number of fields does not match number of ciftis")
        n_elements = inputspreadsheet.ciftiSet.shape
        for i in range(n_elements):
            path = path_prefix + ".voxel" + str(i) + ".inp.out"
            results = self.parse_mplus_results(path, look_for_fields)
            for j in range(len(look_for_fields)):
                # todo how to handle NA's if field not found in results?
                fld = look_for_fields[j]
                value = results.get(fld, naCiftiValue)

                ciftis[j].setPosition(i, value)
            if i > max_todo:
                print("stopping early, testing mode")
                break

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
