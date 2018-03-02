import datetime
import os
import subprocess
from models.cifti import *

import time
import logging
import numpy as np
import threading
import queue
from models.analysis import *
from models.mplus.output_parser import *
import models.mplus_template
import numpy as np
import pandas as pd
import shutil

"""
Note about paths:
System wide default output directory, defined in the config file.

Analysis Output Directory. Each analysis has an output directory, which usually would be a subdirectory of the System Wide Default.

Batch Directory.  When an analysis is executed, a unique directory is created for that execution attempt in:
    {Analysis Output Directory}/batches/{Batch Directory}


"""

class MplusAnalysis(Analysis):
    def __init__(self, config, filename="", saved_data=None):
        super(MplusAnalysis, self).__init__(config, "mplus", filename)
        self.required_config_keys = ['default_maps', 'Base_cifti_for_output', 'MPlus_command', 'output_dir']
        self.limit_by_voxel = -1
        self.limit_by_row = -1
        self.voxelized_column_mappings = []
        self.output_parameters = []
        if saved_data is not None:
            self.process_load_data(saved_data)
            # then we are loading from a saved file.


            self.loaded_from_data = saved_data


    @property
    def output_path(self):
        return self.scrubbed_data_path()

    @property
    def batchOutputDir(self):
        return self.paths.batch_outputs_path()

    def mplus_model_filename_for_voxel(self, voxel_index):

        return "input.voxel%s.inp" % str(voxel_index)

    def dir_name_for_title(self, raw_title):
        return raw_title + str(datetime.datetime.now()).replace(" ", ".").replace(":", ".")

    def go(self, input, missing_tokens_list, progress_callback=None, error_callback=None):

        self.progress_callback = progress_callback

        self.error_callback = error_callback

        #self.paths.create_new_batch()

        self.progressMessage(
            "Beginning analysis job, output will be generated in %s" % self.paths.current_batch_path)

        self.model.title = self.title

        self.input = input

        self.input.cleanMissingValues(missing_tokens_list)

        self.input.save(self.scrubbed_data_path())

        self.needCiftiProcessing = len(self.voxelized_column_mappings) > 0

        if self.needCiftiProcessing:
            return self.runAnalysisWithCiftiProcessing(self.voxelized_column_mappings)
        else:
            return self.runAnalysisWithoutCiftiData()

    def modelInputPathByVoxel(self, voxel_idx):

        model_filename = self.mplus_model_filename_for_voxel(voxel_idx)

        model_input_file_path = self.paths.batch_inputs_path(model_filename)

        return model_input_file_path

    def modelOutputPathByVoxel(self, voxel_idx):

        model_filename = self.mplus_model_filename_for_voxel(voxel_idx)

        model_output_file_path = self.paths.batch_outputs_path(model_filename)

        return model_output_file_path

    def runAnalysisWithCiftiProcessing(self, path_to_voxel_mappings):
        """

        :param path_to_voxel_mappings: an array of tuples (sourcecolumnname, columnnameforvoxel)

        :return:
        """
        start_time = time.time()
        self.progressMessage("Begin generation of csv data files with voxel data")
        self.input.prepare_with_cifti(path_to_voxel_mappings, self.scrubbed_data_path(),
                                      testing_only_limit_to_n_voxels=self.limit_by_voxel,
                                      only_save_columns=self.model.input_column_names_in_order,
                                      limit_by_row=self.limit_by_row)

        time2 = time.time()
        self.progressMessage(
            "Time to read cifti data and prepare csvs with cifti data: %f seconds" % (time2 - start_time))

        if self.cancelling:
            return

        self.progressMessage("Begin generation of MPlus input model files")

        self.generateInputModelsWithVoxel()

        if self.cancelling:
            return

        time3 = time.time()
        self.progressMessage("Time to prepare prepare mplus model files %f seconds" % (time3 - time2))

        if self.cancelling:
            return

        self.progressMessage("Begin execution of the MPlus models")
        self.runAllVoxelBasedModels()

        if self.cancelling:
            return

        time4 = time.time()

        self.progressMessage("Time to run mplus model files %f seconds" % (time4 - time3))

        # load a standard baseline cifti that we will overwrite with our computed data
        #output_cifti = self.base_cifti_for_output()

        #path_template =   self.paths.batch_outputs_path(self.mplus_model_filename_for_voxel("%s") + ".out")

        if self.cancelling:
            return

        # note this code is a little confusing, there are updates happening to the cifti objects
        # while it is return a data frame that contains all the aggregated values

#        aggregated_results = self.model.aggregate_results(self.input.cifti_vector_size,
#                                                          path_template,
#                                                          ["Akaike (AIC)"],
#                                                          [output_cifti],
#                                                          testing_only_limit_to_n_rows=self.limit_by_row)
        time5 = time.time()

 #       self.progressMessage("Time to aggregate mplus results %f seconds" % (time5 - time4))

        if self.cancelling:
            return

        #cifti_output_path = self.scrubbed_data_path() + ".out.dscalar.nii"
        #output_cifti.save(cifti_output_path)
        #time6 = time.time()

        #if self.cancelling:
        #    return

        #aggregated_results.to_csv(cifti_output_path + ".raw.csv", header=True, index=False)
        #self._cifti_output_path = cifti_output_path

        self.progressMessage("TOTAL TIME %f seconds" % (time.time() - start_time))
        return "Ran vectorized model. %i of %s failed" % (self.mplus_exec_errors, self.mplus_exec_count)

    def generateInputModelsWithVoxel(self):
        for i in range(self.input.cifti_vector_size):

            model_input_file_path = self.modelInputPathByVoxel(i)

            datafile_path = self.data_filename + "." + str(i) + ".csv"

            self.model.save_for_datafile(datafile_path, model_input_file_path)

            if self.limit_by_voxel > 0 and i >= self.limit_by_voxel - 1:
                break

    def runAllVoxelBasedModels(self):
        num_threads = self.config.getOptional("mplus_threads", 4)
        if self.limit_by_voxel > 0:
            n = self.limit_by_voxel
        else:
            n = self.input.cifti_vector_size

        sets_of_model_paths = np.array_split(list(range(n)), num_threads)

        threads = []

        self.mplus_exec_counterQueue = queue.Queue()
        self.mplus_exec_count = 0
        self.mplus_exec_errors = 0
        self.mplus_exec_start_time = time.time()
        for i in range(len(sets_of_model_paths)):
            t = threading.Thread(target=self.runMplusForSetOfVoxels, args=[sets_of_model_paths[i]])
            t.start()
            threads.append(t)

        monitor_thread = threading.Thread(target=self.queueMonitor)
        monitor_thread.start()

        for t in threads:
            t.join()

        monitor_thread.join()

    def queueMonitor(self):
        try:
            while True:
                item = self.mplus_exec_counterQueue.get(timeout=5)
                if item is None:
                    break
                count = self.mplus_exec_count + 1
                with threading.Lock():
                    errors_so_far = self.mplus_exec_errors
                    self.mplus_exec_count = count

                if count > 0 and count % 1000 == 0:

                    seconds = time.time() - self.mplus_exec_start_time
                    rate = seconds / count

                    n = self.input.cifti_vector_size
                    remaining = (n - count) * rate / 60
                    models_per_sec = count/seconds
                    self.progressMessage(
                        "Mplus Models executed: %i in %f seconds (%f models/sec).\n\tEstimated remaining time: %f minutes.\n\tMplus errors so far: %s" % (
                            self.mplus_exec_count, seconds, models_per_sec, remaining, errors_so_far))
                self.mplus_exec_counterQueue.task_done()

        except Exception as ex:
            #an exception is expected when the queue is empty and is usually not a problem but other exceptions are possible

            if type(ex) == queue.Empty:
                self.progressMessage("Completed queue of MPlus model file execution.")
            else:
                err_msg = "Exiting Queue Monitor. " + str(ex)
                logging.error(err_msg)
                self.progressMessage("Unexpected error processing MPlus model file queue, execution terminated early. %s" % err_msg)


    def runMplusForSetOfVoxels(self, set_of_voxels):

        for i in set_of_voxels:
            if self.cancelling:
                return

            model_input_file_path = self.modelInputPathByVoxel(i)

            model_output_file_path = self.paths.batch_outputs_path(self.mplus_model_filename_for_voxel(i) + ".out")
            result = self.runMplus(model_input_file_path, model_output_file_path)

            self.mplus_exec_counterQueue.put(i)
            if result.returncode == 1:
                logging.error(
                    "Mplus model run for voxel %i failed\n\tSee file %s.out for details" % (i, model_input_file_path))

                with threading.Lock():
                    self.mplus_exec_errors += 1

                    # todo write to an error queue
            """ sample bad output
            CompletedProcess(args=['/Applications/MplusDemo/mpdemo',
                                   '/Users/David/Documents/projects/mastergui/output/DefaultTitle2017_12_07_11_38_09_024508/input.voxel75.inp',
                                   '/Users/David/Documents/projects/mastergui/output/DefaultTitle2017_12_07_11_38_09_024508/input.voxel75.inp.out'],
                             returncode=1,
                             stdout=b"\n     Mplus VERSION 8 DEMO (Mac)\n     MUTHEN & MUTHEN\n\n     Running input file '/Users/David/Documents/projects/mastergui/output/DefaultTitle2017_12_07_11_38_09_024508/input.voxel75.inp'...\n\n An error has occurred, refer to '/Users/David/Documents/projects/mastergui/outp\n ut/DefaultTitle2017_12_07_11_38_09_024508/input.voxel75.inp.out'\n")

            """
            # todo monitor these for errors
            # ok = self.evalMplusStdOut(result)

    def evalMplusStdOut(self, result):
        # todo monitor these for errors
        something_bad_happened = False
        if something_bad_happened:
            raise ValueError("Something bad is in the mplus output")

        return True

    def runAnalysisWithoutCiftiData(self):
        model_filename = "input.inp"
        model_input_file_path = os.path.join(self.batchOutputDir, model_filename)
        model_output_file_path = model_input_file_path + ".out"

        nonimaging_data_path = self.scrubbed_data_path()

        self.input.save(nonimaging_data_path, self.model.input_column_names_in_order)

        self.model.save_for_datafile(self.data_filename, model_input_file_path)

        result = self.runMplus(model_input_file_path)

        self.mplus_stdout = str(result.stdout, 'utf-8')

        with open(model_output_file_path, "r") as f:
            mplus_output_contents = f.read()

        return mplus_output_contents

    @property
    def cifti_output_path(self):
        if hasattr(self, "_cifti_output_path"):
            return self._cifti_output_path
        else:
            return ""

    def runMplus(self, model_input_file_path, model_output_file_path=""):
        # launch mplus

        # todo safety check this in case of rogue yml input!

        if len(model_output_file_path)==0:
            model_output_file_path = model_input_file_path + ".out"
        cmd = self.config._data["MPlus_command"] + " " + model_input_file_path

        result = subprocess.run([self.config._data["MPlus_command"],
                                 model_input_file_path,
                                 model_output_file_path], stdout=subprocess.PIPE)

        return result

    def module_specific_save_data(self, save_data):
        save_data["voxelized_column_mappings"] = self.voxelized_column_mappings

        save_data["current_model"] = self.model.to_string()

        save_data["additional_rules"] = self.model.additional_rule_save_data

        save_data["output_parameters"] = self.output_parameters

        if hasattr(self, "input"):
            save_data["input_data_path"] = self.input.path




#        save_data["batchOutputDir"] = self.batchOutputDir

    def process_load_data(self, load_data):
        super(MplusAnalysis,self).process_load_data(load_data)
        # todo load all the attributes from the save file
        if "input_data_path" in load_data:
            self.input_data_path = load_data["input_data_path"]

        if "voxelized_column_mappings" in load_data:
            self.voxelized_column_mappings = load_data["voxelized_column_mappings"]

            if type(self.voxelized_column_mappings) == list:
                for i in range(len(self.voxelized_column_mappings)):
                    # by convention we are treating the mappings as tuples (from_col_name, to_col_name)
                    # but json reads them in as lists to we are just converting each mapping from a list to a tuple here
                    self.voxelized_column_mappings[i] = tuple(self.voxelized_column_mappings[i])


        if "template" in load_data:

            self.template = models.mplus_template.MplusTemplate(load_data['template'])

            self.model = models.mplus_model.MplusModel()
            self.model.loadFromString(self.template.rawModel)
            self.updateModelVoxelizedList()
            if "additional_rules" in load_data:
                rules = load_data["additional_rules"]
                for key, rule_data in rules.items():
                    self.model.add_rule(rule_data[0],rule_data[1],rule_data[2])

        if "batchTitle" in load_data:
            self.batchTitle = load_data["batchTitle"]

        if "output_parameters" in load_data:
            self.output_parameters = load_data["output_parameters"]
            if not type(self.output_parameters)==list:
                self.output_parameters = []

    def addVoxelizedColumn(self, from_column_of_paths, to_new_column_name):
        t = (from_column_of_paths, to_new_column_name)
        if not t in self.voxelized_column_mappings:
            self.voxelized_column_mappings.append(t)

        #keep the underlying model in sink
        self.updateModelVoxelizedList()

    def removeVoxelizedColumn(self, from_column_of_paths, to_new_column_name):
        t = (from_column_of_paths, to_new_column_name)
        if t in self.voxelized_column_mappings:
            self.voxelized_column_mappings.remove(t)

    def voxelizedColumnNames(self):
        return [m[1] for m in self.voxelized_column_mappings]

    def cancelAnalysis(self):
        """attempt to cancel the running analyis"""
        self.cancelling = True
        self.input.cancelAnalysis()

    def updateModelVoxelizedList(self):
        """the mplus model has a separate list of which variable/columns have been voxelized for its internal functionality
        but this analysis class is the final source of truth for that info (to facillitate saving/loading).  this analysis class
        needs to make sure the underlying mplus model has the correct voxelization information"""
        if hasattr(self,'model'):
            self.model.voxelized_column_names_in_order = self.voxelizedColumnNames()

    def updateModel(self, options, non_original_data_columnlist):
        self.updateModelVoxelizedList()
        return self.model.apply_options(options, non_original_data_columnlist)


    def aggregate_results(self,path_template="", n_elements = 0):
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

        if len(self.output_parameters) == 0:
            raise ValueError("No output parameters are selected.")

        if n_elements == 0:
            # todo this override is not a great compromise but is making it easier to
            # rerun value extractions without recomputing the size of all ciftis.
            n_elements = 91282  # set to the default value

        if len(path_template)==0:
            path_template = self.paths.batch_outputs_path("input.voxel%s.inp.out")

        outputs = MplusOutputSet(path_template)

        self.outputset = outputs

        results = outputs.extract(self.output_parameters, n_elements)

        results.to_csv(self.paths.batch_cifits_path("extracted.csv"), index=False)

        self.generate_mask_ciftis(n_elements)

        self.generate_ciftis_from_dataframe(results)

        return results

    def generate_mask_ciftis(self, n_elements):
        """we display voxel level errors and problems by generating 'mask' ciftis of 0's and 1s
        to allow easy filtering by the user in ConnectomeWorkbench


        Build up a dataframe of masks, 1 row per voxel, each column will be turned into a cifti

        Different masks that we generate include:
        a:  1 if no problem at all (clean as a whistle), 0, if ANY problem.
        b. 1 if no convergence , 0 if clean or problem [cuz we want the non-convergence issues specifically to stand out]
        c. untrustworthy 1, 0 otherwise
        d. per parameter/variable, untrustworthy 1, 0 otherwise
        e. per parameter/variable and type of warning/error
        """

        #case 1: 1 if no problem at all (clean as a whistle), 0, if ANY problem.
        no_problem_vector = np.zeros(n_elements) + 1
        no_problem_vector[self.outputset.any_errors] = 0

        masks = pd.DataFrame(no_problem_vector, columns = ["No_Problems"])



        #case c. untrustworthy 1, 0 otherwise
        untrustworthy_vector = np.zeros(n_elements)
        untrustworthy_vector[self.outputset.untrustworthies]=1
        masks["Untrustworthy"] = untrustworthy_vector

        self.generate_ciftis_from_dataframe(masks)


    def removeBatch(self,path):
        shutil.rmtree(path)