import glob
import os
from collections import defaultdict
import re
import numpy as np
import pandas as pd
import threading

Model_Fit_Information_Label = "MODEL FIT INFORMATION"
Model_Results_Label = "MODEL RESULTS"
Standarized_Model_Results_Label = "STANDARDIZED MODEL RESULTS"
key_delimiter = "|"

class MplusOutput():
    def __init__(self,path, limit_to_keys = []):
        #debug with tests/sample.mplus.modelwarning.out
        self.limited_parse = len(limit_to_keys) > 0
        if self.limited_parse:
            self.limit_to_keys = limit_to_keys
            self.limit_to_sections = [key.split("|")[0] for key in limit_to_keys]
        else:
            self.limit_to_keys = []
            self.limit_to_sections = []

        self.path = path
        self.warnings = []
        self.load()

    def load(self):

        #we are calling a 'heading' an all caps line with no indentation, - also allowed as in R-SQUARED
        heading_detector = re.compile("^[A-Z][A-Z \-]*$")

        warning_detector = re.compile("^\*\*\* WARNING")
        self.sections = {}
        self.data = {}
        last_section = ""
        last_section_lines = []
        in_warning = False
        in_section = False
        last_section_is_warning = False

        #all_lines = []


        with open(self.path, "r") as f:
            all_lines = f.readlines()

        for line in all_lines:

            new_section_detected = False

            if heading_detector.match(line) or warning_detector.match(line):
                new_section_detected = True
                self.process_section_contents(last_section, last_section_lines)
                last_section = line.strip()
                last_section_lines = []
            else:
                if len(last_section)>0:
                    last_section_lines.append(line)
            #all_lines.append(line)



        self.lines = all_lines


    def process_section_contents(self,  last_section, last_section_lines):
        if last_section:
            if last_section[:10]=="***WARNING":
                self.warnings.append(" ".join([last_section] + last_section_lines))
            else:
                if self.limited_parse and not last_section in self.limit_to_sections:
                    #print("%s not in %s" % (last_section, str(self.limit_to_sections)))
                    return

                if last_section == Model_Fit_Information_Label:
                    self.process_model_fit(last_section_lines)
                elif last_section == Model_Results_Label:
                    self.process_results_table(Model_Results_Label, last_section_lines)
                elif last_section == Standarized_Model_Results_Label:
                    self.process_results_table(Standarized_Model_Results_Label, last_section_lines)
                else:
                    self.sections[last_section] = last_section_lines

    def process_model_fit(self, section_lines):

        """Sample contents of this section in an mplus output file:

        MODEL FIT INFORMATION

        Number of Free Parameters                       10

        Loglikelihood

                  H0 Value                          22.303
                  H1 Value                          43.711

        Information Criteria

                  Akaike (AIC)                     -24.606
                  Bayesian (BIC)                   -33.620
                  Sample-Size Adjusted BIC         -60.292
                    (n* = (n + 2) / 24)

        SRMR (Standardized Root Mean Square Residual)

                  Value                              0.453


        """
        context_stack = []
        section_data = {}
        # rrr = re.compile('.*\s+([+-]?([0-9]*[.])?[0-9]+)')
        # rrr = re.compile('([+-]?[0-9]*[.]?[0-9]+)')

        number_matcher = re.compile('([+-]?[0-9]*[.]?[0-9]+)')

        for line in section_lines:
            #line = line.strip()
            if line.strip(): #ignore empty lines
                first = line[0]
                is_indented = first == " " or first == "\t"

                parts = line.split(" ")
                parts = [p for p in parts if p]
                ends_in_number = number_matcher.match(parts[-1])
                if ends_in_number:

                    #try:
                    n = float(ends_in_number.groups()[0])
                    keyname = " ".join(parts[:-1])


                    keyname = key_delimiter.join(context_stack + [keyname])

                    self.data[Model_Fit_Information_Label + key_delimiter + keyname] = n
                    section_data[keyname] = n
                    #except Exception as e:
                        #print("converting to number didn't work")
                else:
                    if not is_indented:
                        context_stack = [line.strip()]


                        #
                #     stripped_line = line.strip()
                #     if stripped_line:
                #         print("ever happen?")
                #         context_stack.append(line.strip())
                #         print(context_stack)
        self.sections[Model_Fit_Information_Label] = section_data

    def process_results_table(self, title, lines):
        """
            Parse the MODEL RESULTS section

            Sample Mplus output contents:

            MODEL RESULTS

                                                                Two-Tailed
                                Estimate       S.E.  Est./S.E.    P-Value

             Means
                NUC_ACC_VI         0.067      0.025      2.709      0.007
                PC6                0.016      0.004      4.287      0.000
                PC1               -0.026      0.032     -0.820      0.412
                VOX               -0.117      0.123     -0.951      0.342
                PGS                0.478      0.087      5.494      0.000

             Variances
                NUC_ACC_VI         0.002      0.001      2.449      0.014
                PC6                0.000      0.000      2.449      0.014
                PC1                0.003      0.001      2.449      0.014
                VOX                0.046      0.019      2.449      0.014
                PGS                0.023      0.009      2.449      0.014

        """
        #print("Begin parse table "  + title)
        first_char_finder  = re.compile('([A-Z])')
        column_names = []
        section_data = {}
        ws = re.compile('\s+')
        for line in lines:
            m = re.search(first_char_finder,line)
            if m:
                idx = m.start()
                #print("Start index %d" % idx)
                #print(line)
                if idx == 20:
                    column_names = re.split(ws,line.strip())
                elif idx == 1:
                    stat_type = line.strip()
                elif idx == 4:
                    #print("it was idx4")
                    #print(line)
                    parts = re.split(ws, line.strip())
                    if len(parts) == 5:
                        stat_name = parts[0]
                        keyprefix = key_delimiter.join([title, stat_type,stat_name])
                        for i in range(1,len(parts)):
                            keyname = keyprefix + key_delimiter + column_names[i-1]
                            try:
                                value = float(parts[i])
                                self.data[keyname] = value
                                section_data[keyname] = value
                            except:
                                print("Error converting value for key %s in file %s. Line was:\n %s" % (keyname, self.path, line))

        self.sections[title] = section_data

    def terminated_normally(self):
        idx = -1
        try:
            idx = self.lines.index("THE MODEL ESTIMATION TERMINATED NORMALLY\n")
        except Exception as e:
            print("error seeking")

        return idx>=0



    def print_report(self):
        print("Analysis of Mplus Output " + self.path)
        if Model_Fit_Information_Label in self.sections:
            for k,v in self.sections[Model_Fit_Information_Label].items():
                print("%s: %s" % (k,v))


        print("Begin all keys flattenned:")
        for k,v in self.data.items():
            print("%s: %s" % (k, v))
        print("Terminated normally?")
        print(self.terminated_normally())


class MplusOutputSet():
    def __init__(self, path_template):
        self.path_template = path_template
        self.count=0
    # def load_all(self):
    #     search_path = os.path.join(self.path, "*.out")
    #     files = glob.glob(search_path)
    #     stats = defaultdict(int)
    #
    #     for path in files:
    #         print("reading file")
    #         f = MplusOutput(path)
    #         self.count += 1
    #         if f.terminated_normally():
    #             stats["terminated_normally"] += 1
    #             warnings = f.warnings
    #             for w in warnings:
    #                 stats[w] += 1
    #
    #     self.stats = stats
    #
    #     return stats

    def extract(self, keys_to_extract, n_voxels_expected = 91282):
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
        if n_voxels_expected == 0:
            # todo this override is not a great compromise but is making it easier to
            # rerun value extractions without recomputing the size of all ciftis.
            n_voxels_expected = 91282  # set to the default value

        all_found_results = np.zeros((n_voxels_expected, len(keys_to_extract)), dtype=np.float32)

        all_found_results[:] = np.nan
        not_found_counts = {}
        warnings = {}



        num_threads = 4

        sets_of_voxel_indexes = np.array_split(list(range(n_voxels_expected)), num_threads)

        #places for the threads to park their error findings without fighting to access the
        #same data structures too much
        self.warnings_sets = []
        self.notfound_sets = []

        threads = []

        for i in range(len(sets_of_voxel_indexes)):
            t = threading.Thread(target=self.loadForSetOfVoxels, args=[sets_of_voxel_indexes[i], keys_to_extract, all_found_results])
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        if False:
            for i in range(n_voxels_expected):
                path = self.path_template % i  # + ".voxel" + str(i) + ".inp.out"

                o = MplusOutput(path, keys_to_extract)

                for w in o.warnings:
                    warnings[w] = warnings.get(w,[]) + [i]

                #for k in o.data.keys():
                #    print(k)
                for key_i in range(len(keys_to_extract)):
                    key = keys_to_extract[key_i]
                    if key in o.data:
                        all_found_results[i, key_i] = o.data[key]
                    else:
                        not_found_counts[key] = not_found_counts.get(key,0)+1
                        #print("Value not found for key %s in file %s" % (key, path)) #todo decide how to handle

        #now reduce the warnings and notfounds found by each thread
        for warningset in self.warnings_sets:
            for k,v in warningset.items():
                warnings[k] = warnings.get(k,[]) + v

        for notfoundset in self.notfound_sets:
            for k,v in notfoundset.items():
                not_found_counts[k] = not_found_counts.get(k,0)  + v

        warnings_counts = {k:len(v) for k,v in warnings.items()}

        self.warnings = warnings
        self.warning_counts = warnings_counts

        self.not_found_counts = not_found_counts
        column_names = keys_to_extract
        all_results_df = pd.DataFrame(all_found_results, columns=column_names)

        return all_results_df

    def loadForSetOfVoxels(self, voxel_indexes, keys_to_extract, all_found_results):

        not_found_counts = {}
        warnings = {}

        for i in voxel_indexes:
            path = self.path_template % i  # + ".voxel" + str(i) + ".inp.out"

            o = MplusOutput(path, keys_to_extract)

            for w in o.warnings:
                warnings[w] = warnings.get(w,[]) + [i]

            #for k in o.data.keys():
            #    print(k)
            for key_i in range(len(keys_to_extract)):
                key = keys_to_extract[key_i]
                if key in o.data:
                    with threading.Lock():
                        all_found_results[i, key_i] = o.data[key]
                else:
                    not_found_counts[key] = not_found_counts.get(key,0)+1
                    #print("Value not found for key %s in file %s" % (key, path)) #todo decide how to handle

        with threading.Lock():
            self.notfound_sets.append(not_found_counts)
            self.warnings_sets.append(warnings)

