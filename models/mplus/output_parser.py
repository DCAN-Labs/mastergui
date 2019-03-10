import glob
import os
from collections import defaultdict
import re
import numpy as np
import pandas as pd
import threading
import re

Model_Fit_Information_Label = "MODEL_FIT_INFORMATION"
Model_Results_Label = "MODEL_RESULTS"
Standarized_Model_Results_Label = "STANDARDIZED_MODEL_RESULTS"
key_delimiter = "-"
Model_Termination_Section_Label = "THE_MODEL_ESTIMATION_TERMINATED_NORMALLY"
Sample_Statistics_Label = "SAMPLE_STATISTICS"

# for stripping keys of values that we don't want in filenames
filename_unfriendly_character_detector = re.compile('[^0-9a-zA-Z\-]+')

# many mplus model termination warnings are identical except for a condition number that we rarely need, use this to remove them.
Condition_Number_Mask = re.compile("(.*HE CONDITION NUMBER IS )\s*([0-9\.D\-]*)\.")

"""Termination Warning example:   sometimes Mplus modes do terminate successfully but have warning messages under the heading
THE MODEL ESTIMATION TERMINATED NORMALLY

An example:
THE MODEL ESTIMATION TERMINATED NORMALLY

     THE STANDARD ERRORS OF THE MODEL PARAMETER ESTIMATES MAY NOT BE
     TRUSTWORTHY FOR SOME PARAMETERS DUE TO A NON-POSITIVE DEFINITE
     FIRST-ORDER DERIVATIVE PRODUCT MATRIX.  THIS MAY BE DUE TO THE STARTING
     VALUES BUT MAY ALSO BE AN INDICATION OF MODEL NONIDENTIFICATION.  THE
     CONDITION NUMBER IS      -0.133D-17.  PROBLEM INVOLVING THE FOLLOWING PARAMETER:
     Parameter 19, ROI_52_21_23_TO_ROI_LASEG


     WARNING:  THE LATENT VARIABLE COVARIANCE MATRIX (PSI) IS NOT POSITIVE
     DEFINITE.  THIS COULD INDICATE A NEGATIVE VARIANCE/RESIDUAL VARIANCE FOR A
     LATENT VARIABLE, A CORRELATION GREATER OR EQUAL TO ONE BETWEEN TWO LATENT
     VARIABLES, OR A LINEAR DEPENDENCY AMONG MORE THAN TWO LATENT VARIABLES.
     CHECK THE TECH4 OUTPUT FOR MORE INFORMATION.
     PROBLEM INVOLVING VARIABLE S.

This is distinct situation from some other kinds of warnings that sometimes appear in Mplus model output, in the form

*** WARNING {{and then could vary from here-ish on out}}

When we parse we track these 2 kinds of warning separately.

MPlusOutputSet.termination_warnings is the first kind of warning, under the "Model Termination header"
MPlusOutputSet.warnings is the "*** WARNING" kind of warning


"""


class MplusOutput():
    def __init__(self, path, limit_to_keys=[]):
        # debug with tests/sample.mplus.modelwarning.out
        self.limited_parse = len(limit_to_keys) > 0
        self.sample_lines = []
        self.rsquare_lines = []
        self.lines = []
        if self.limited_parse:
            self.limit_to_keys = limit_to_keys
            self.limit_to_sections = [key.split(key_delimiter)[0] for key in limit_to_keys]
            # if not Model_Termination_Section_Label in self.limit_to_sections:
            #     self.limit_to_keys.append(Model_Termination_Section_Label)
        else:
            self.limit_to_keys = []
            self.limit_to_sections = []

        self.path = path
        self.warnings = []

        self.load()
        #self.process_sample_stats()

    def load(self):

        # we are calling a 'heading' an all caps line with no indentation, - also allowed as in R-SQUARED
        heading_detector = re.compile("^[A-Z][A-Z \-]*$")

        warning_detector = re.compile("^\*\*\* WARNING")
        self.sections = {}
        self.data = {}
        self.numberErrorsByKey = {}
        last_section = ""
        last_section_lines = []
        in_warning = False
        in_section = False
        self.terminated_normally = False
        self.had_model_warnings = False
        self.model_warning_content = ""
        self.any_error = False
        self.file_read_error = False

        last_section_is_warning = False


        try:
            with open(self.path, "r") as f:
                all_lines = f.readlines()
        except Exception as e:
            self.any_error = True
            self.file_read_error = True
            self.lines = []
            return

        for line in all_lines:

            new_section_detected = False
            # what is heading detector matching for to get wat appear to be the first 30 lines of all lines
            # last_section_lines is the input file for mplus, generated in the model builder.
            if heading_detector.match(line) or warning_detector.match(line):
                new_section_detected = True
                self.process_section_contents(last_section, last_section_lines)
                last_section = self.cleanKey(line.strip())
                last_section_lines = []
            else:
                if len(last_section) > 0:
                    last_section_lines.append(line)
        # All lines contains the entirety of the output file
        self.lines = all_lines
        self.process_sample_stats(all_lines)
        self.process_rsquare(all_lines)

        if self.terminated_normally:
            if len(self.model_convergence_warnings) > 0:
                self.any_error = True
        else:
            self.any_error = True

    def process_section_contents(self, last_section, last_section_lines):
        if last_section:
            if last_section[
               :10] == "___WARNING":  # in the original MPlus this would have been ***WARNING but we have replaced non alphanumerics with _ at this point
                self.warnings.append(" ".join([last_section] + last_section_lines))
            else:
                if self.limited_parse and not last_section in self.limit_to_sections:
                    # print("%s not in %s" % (last_section, str(self.limit_to_sections)))
                    if not last_section == Model_Termination_Section_Label:
                        return

                if last_section == Sample_Statistics_Label:
                    print('\n'*60, ' it fired '*100)

                elif last_section == Model_Fit_Information_Label:
                    self.process_model_fit(last_section_lines)
                elif last_section == Model_Results_Label:
                    self.process_results_table(Model_Results_Label, last_section_lines)
                elif last_section == Standarized_Model_Results_Label:
                    self.process_results_table(Standarized_Model_Results_Label, last_section_lines)
                elif last_section == Model_Termination_Section_Label:
                    self.process_model_termination_section(last_section_lines)
                else:
                    self.sections[last_section] = last_section_lines

    def process_sample_stats(self, every_friggen_line):
        """
        :param every_friggen_line: this is gathered from self.all_lines
        and is an mplus output/input text file that has been read into a
        list of strings.
        :return: Places sample mean statistics into check-menu for output
        params under the execute tab in mplus analysis.
        analysis.
        """
        # TODO: add in the covariance and other sample statistics into
        # TODO: the self.data dictionary below
        lines = every_friggen_line
        # Headings that we're searching for in the mplus output
        # We anything that is 2 lines below these headings corresponds
        # To the variables referenced
        things_to_check = ['Means', 'Covariances', 'Correlations']

        main_heading = 'SAMPLE STATISTICS'
        sub_heading = 'ESTIMATED SAMPLE STATISTICS'
        end_section = 'UNIVARIATE SAMPLE STATISTICS'
        start_index = None
        stop_index = None

        # Finding the start and stop of the sample input
        for index, mplus_line in enumerate(lines):
            if sub_heading in mplus_line:
                start_index = index
            if end_section in mplus_line:
                stop_index = index - 1


        self.sample_lines = lines[start_index: stop_index]

        data = {}
        covar_dict = {}
        corr_dict = {}
        means_dict = {}
        for thing in things_to_check:
            for i, sample_line in enumerate(self.sample_lines):

                if thing in sample_line:

                    if thing is "Means":

                        variables = self.sample_lines[i +1].strip('\n').split()
                        values = self.sample_lines[i+3].strip('\n').split()
                        for ix, var in enumerate(variables):

                            means_dict['Estimated_Mean_' + var] = values[ix]

        self.sections['Estimated_Means'] = means_dict
        for key, value in means_dict.items():
            # self.sections['STANDARDIZED_MODEL_RESULTS'][key] = value
            # self.sections['MODEL_RESULTS']['MODEL_RESULTS    ' + key] = value
            self.data['MODEL_RESULTS_ESTIMATED_MEANS_' + key] = value


    def process_rsquare(self, every_friggen_line):
        """
        :param every_friggen_line: this is gathered from self.all_lines
        and is an mplus output/input text file that has been read into a
        list of strings.
        :return: Places sample mean statistics into check-menu for output
        params under the execute tab in mplus analysis.
        analysis.
        """
        # TODO: add in the covariance and other sample statistics into
        # TODO: the self.data dictionary below
        lines = every_friggen_line
        # Headings that we're searching for in the mplus output
        # We anything that is 2 lines below these headings corresponds
        # To the variables referenced

        main_heading = 'R-SQUARE'
        second_heading = ['Variable', 'Estimate', 'S.E.', 'Est./S.E', 'P-Value']
        end_section = 'QUALITY OF NUMERICAL RESULTS'
        start_index = None
        stop_index = None
        self.store = []
        # Finding the start and stop of the sample input
        for index, mplus_line in enumerate(lines):
            if main_heading in mplus_line:
                start_index = index
            if end_section in mplus_line:
                stop_index = index - 1

        self.rsquare_lines = lines[start_index: stop_index]
        # I hate this,  the formatting of this mplus output is
        # all over the place. Every solution is a hacky one.
        is_second_heading = 0
        for index, line in enumerate(self.rsquare_lines):
            if is_second_heading < 5:
                for each in second_heading:
                    if each in line:
                        is_second_heading += 1
            elif is_second_heading == 5:
                store_dict = {}
                variable_dict = {} 
                var_name = None
                for line_index, line_content in enumerate(line.split()):
                    print(line_index, line_content)
                    if line_index == 0:
                        var_name = line_content
                    elif line_index > 0:
                        variable_dict[second_heading[line_index]] = line_content
                if var_name:
                    store_dict[var_name] = variable_dict
                if store_dict:
                    self.store.append(store_dict)
        
        for each in self.store:
            for key in each.keys():
                for k, value in each[key].items():
                    sub = '/.'
                    ksub = re.sub(sub, '', k)
                    keysub = re.sub(sub, '', key)
                    self.data['STANDARDIZED_MODEL_RESULTS-R-SQUARE_' + str(ksub) + '_' + str(keysub)] = value

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
            # line = line.strip()
            if line.strip():  # ignore empty lines
                first = line[0]
                is_indented = first == " " or first == "\t"

                parts = line.split(" ")
                parts = [p for p in parts if p]
                ends_in_number = number_matcher.match(parts[-1])
                if ends_in_number:

                    try:
                        n = float(ends_in_number.groups()[0])
                        keyname = " ".join(parts[:-1])

                        keyname = key_delimiter.join(context_stack + [keyname])

                        self.setDataValue(Model_Fit_Information_Label + key_delimiter + keyname, n)

                        section_data[keyname] = n
                    except Exception as e:

                        if self.limited_parse:
                            if keyname in self.limit_to_keys:
                                self.logNumberParsingError(keyname)
                                # otherwise we can just ignore it
                        else:
                            self.logNumberParsingError(keyname)

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

    def logNumberParsingError(self, keyName):

        with threading.Lock():
            self.numberErrorsByKey[keyName] = True

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
        # print("Begin parse table "  + title)
        first_char_finder = re.compile('([A-Z])')
        column_names = []
        section_data = {}
        ws = re.compile('\s+')
        for line in lines:
            m = re.search(first_char_finder, line)
            if m:
                idx = m.start()
                # print("Start index %d" % idx)
                # print(line)
                if idx == 20:
                    column_names = re.split(ws, line.strip())
                elif idx == 1:
                    stat_type = line.strip()
                elif idx == 4:
                    # print("it was idx4")
                    # print(line)
                    parts = re.split(ws, line.strip())
                    # if len(parts) == 5:
                    stat_name = parts[0]
                    keyprefix = key_delimiter.join([title, stat_type, stat_name])
                    for i in range(1, len(parts)):
                        keyname = keyprefix + key_delimiter + column_names[i - 1]
                        try:
                            value = float(parts[i])
                            self.setDataValue(keyname, value)
                            section_data[keyname] = value
                        except:

                            if self.limited_parse:
                                if keyname in self.limit_to_keys:
                                    self.logNumberParsingError(keyname)
                                    # otherwise we can just ignore it
                            else:
                                self.logNumberParsingError(keyname)

        #self/.process_sample_stats(lines)

        self.sections[title] = section_data
        print("SECTION DATA**************************", section_data)

    def cleanKey(self, key):
        """replace filename unfriendly characters with _ """
        return re.sub(filename_unfriendly_character_detector, '_', key)

    def setDataValue(self, key, value):
        """the point of this method is to throw an error if the key already exists.
        the parsing scheme assumes that our key mechanism uniquely identifies each value in mplus
        but as we don't control the mplus output and can't be sure this serves as a safety check"""

        key = self.cleanKey(key)

        if key in self.data:
            raise ValueError("Key *s already exists" % key)
        else:
            self.data[key] = value

    def process_model_termination_section(self, lines):

        self.terminated_normally = True
        warnings = []
        warning = ""
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                if len(warning) > 0:
                    warning += " "
                warning += line
            else:
                if len(warning) > 0:
                    warnings.append(warning)
                    warning = ""
        if len(warning) > 0:
            warnings.append(warning)

        r3 = re.compile("(.*HE CONDITION NUMBER IS )([0-9\.D\-]*)\.")
        r3 = re.compile("(.*HE CONDITION NUMBER IS )\s*[0-9\.D\-]*\.")

        # remove the condition # that is unnececessarily for our purposes making warnings unique.
        for i in range(len(warnings)):
            warnings[i] = re.sub(Condition_Number_Mask, r'\1 xxxx', warnings[i])

        condensed = "\n".join(warnings)

        if len(condensed) > 0:
            self.had_model_warnings = True
            self.model_warning_content = condensed
        self.model_convergence_warnings = warnings

    def print_report(self):
        print("Analysis of Mplus Output " + self.path)
        if Model_Fit_Information_Label in self.sections:
            for k, v in self.sections[Model_Fit_Information_Label].items():
                print("%s: %s" % (k, v))

        print("Begin all keys flattenned:")
        for k, v in self.data.items():
            print("%s: %s" % (k, v))
        print("Terminated normally?")
        print(self.terminated_normally())


class MplusOutputSet():
    def __init__(self, path_template):
        self.path_template = path_template
        self.count = 0

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

    def extract(self, keys_to_extract, n_voxels_expected=91282):
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

        self.warnings_sets = []
        self.notfound_sets = []
        self.not_terminated_voxels = []
        self.termination_warning_sets = []
        self.any_errors = []
        self.untrustworthies = []

        use_threads = True

        # this code to disable the multithreading in this step is just to facilliate debugging.
        # in production, use_threads should be true for best performance
        if use_threads:
            num_threads = 4

            sets_of_voxel_indexes = np.array_split(list(range(n_voxels_expected)), num_threads)

            # places for the threads to park their error findings without fighting to access the
            # same data structures too much

            threads = []

            for i in range(len(sets_of_voxel_indexes)):
                t = threading.Thread(target=self.loadForSetOfVoxels,
                                     args=[sets_of_voxel_indexes[i], keys_to_extract, all_found_results])
                t.start()
                threads.append(t)

            for t in threads:
                t.join()
        else:
            self.loadForSetOfVoxels(list(range(n_voxels_expected)), keys_to_extract, all_found_results)

        # now reduce the warnings and notfounds found by each thread
        for warningset in self.warnings_sets:
            for k, v in warningset.items():
                warnings[k] = warnings.get(k, []) + v

        for notfoundset in self.notfound_sets:
            for k, v in notfoundset.items():
                not_found_counts[k] = not_found_counts.get(k, 0) + v

        termination_warnings = {}
        for terminationwarningset in self.termination_warning_sets:
            for k, v in terminationwarningset.items():
                if k in termination_warnings:
                    termination_warnings[k] = termination_warnings[k] + v
                else:
                    termination_warnings[k] = v

        warnings_counts = {k: len(v) for k, v in warnings.items()}

        self.warnings = warnings
        self.warning_counts = warnings_counts

        self.not_found_counts = not_found_counts
        self.termination_warnings = termination_warnings

        column_names = keys_to_extract
        all_results_df = pd.DataFrame(all_found_results, columns=column_names)

        return all_results_df

    def loadForSetOfVoxels(self, voxel_indexes, keys_to_extract, all_found_results):

        not_found_counts = {}
        warnings = {}
        not_terminated_normally = []
        termination_warnings = {}
        any_errors = []
        untrustworthies = []
        for i in voxel_indexes:
            path = self.path_template % i  # + ".voxel" + str(i) + ".inp.out"

            o = MplusOutput(path, keys_to_extract)

            for w in o.warnings:
                warnings[w] = warnings.get(w, []) + [i]

            # for k in o.data.keys():
            #    print(k)
            for key_i in range(len(keys_to_extract)):
                key = keys_to_extract[key_i]
                if key in o.data:
                    with threading.Lock():
                        all_found_results[i, key_i] = o.data[key]
                else:
                    not_found_counts[key] = not_found_counts.get(key, 0) + 1
                    # print("Value not found for key %s in file %s" % (key, path)) #todo decide how to handle
            if not o.terminated_normally:
                not_terminated_normally.append(i)
            else:
                untrustworthies.append(i)
                if o.model_warning_content in termination_warnings:
                    termination_warnings[o.model_warning_content].append(i)
                else:
                    termination_warnings[o.model_warning_content] = [i]

            if o.any_error:
                any_errors.append(i)

        with threading.Lock():
            self.notfound_sets.append(not_found_counts)
            self.warnings_sets.append(warnings)
            self.not_terminated_voxels += not_terminated_normally
            self.termination_warning_sets.append(termination_warnings)
            self.any_errors += any_errors
            self.untrustworthies += untrustworthies

if __name__ == "__main__":
    ugly_baby = '/mnt/max/shared/projects/NHP/HFD/Experiments/cortical_thickness/subjects/9172018/testing/batches/2018-12-07.14.03.28.776151/outputs/input.voxel0.inp.out'

    test_mplus_output = MplusOutput(path=ugly_baby)
    test_mplus_output.path = 'mplus_output.txt'
    for line in test_mplus_output.lines:
        print(line.strip('\n'))

    #print(test_mplus_output.sections)
    test_mplus_output.data

    #test_mplus_output.process_sample_stats()
    x = test_mplus_output.sample_lines
    for each in x:
        print(each)


