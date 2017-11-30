import datetime
import os
import subprocess
from models.cifti import *
import re
import time
import logging
import numpy as np
import threading
import queue


class MplusAnalysis:
    def __init__(self, config):
        self.config = config

    def missingRequiredConfigKeys(self):
        keys = ['default_maps', 'Base_cifti_for_output', 'MPlus_command', 'output_dir']
        missing_keys = [k for k in keys if not k in self.config._data]
        return missing_keys

    def updateGeneratedMPlusInputFile(self, save_to_path, add_voxel_column_name=None):
        columns = self.input.columnnames()
        if add_voxel_column_name is not None:
            columns.append(add_voxel_column_name)
        self.model.set_column_names(columns)

        #        generated_mplus_model = self.model.to_string()
        #        self.generatedModelViewer.setText(generated_mplus_model)

        if len(save_to_path) > 0:
            with open(save_to_path, "w") as f:
                f.write(self.model.to_string())

    @property
    def filename_prefix(self):
        # make data file with non alphanumeric characters replaced with _
        return "input"  # self.model.title_for_filename

    @property
    def base_output_path(self):
        return os.path.join(self.batchOutputDir, self.filename_prefix)

    @property
    def data_filename(self):
        return "input.csv"

    @property
    def output_path(self):
        return os.path.join(self.batchOutputDir, self.data_filename)

    @property
    def output_dir(self):
        return self.config._data.get("output_dir", "")

    @property
    def batchOutputDir(self):
        return os.path.join(self.output_dir, self.batchTitle)

    def input_file_name_for_voxel(self, voxel_index):
        return "%s.voxel%s.inp" % (self.filename_prefix, str(voxel_index))

    def dir_name_for_title(self, raw_title):
        return raw_title + str(datetime.datetime.now()).replace(" ", ".").replace(":", ".")

    def setBatchTitle(self, raw_title):
        self.batchTitle = re.sub('[^0-9a-zA-Z]+', '_', self.dir_name_for_title(raw_title))

    def go(self, model, title, input, missing_tokens_list, testing_only_limit_to_n_rows=3, needsCiftiProcessing=True):

        if len(title) == 0:
            title = "Untitled"

        self.setBatchTitle(title)

        # create a directory composed of the analysis title and a timestamp into which all the writing will happen

        os.mkdir(self.batchOutputDir)

        title = self.batchTitle

        self.model = model

        self.model.title = title

        self.input = input

        self.input.save_cleaned_data(self.output_path, missing_tokens_list)

        self.needCiftiProcessing = needsCiftiProcessing

        if self.needCiftiProcessing:
            return self.runAnalysisWithCiftiProcessing(testing_only_limit_to_n_rows)
        else:
            return self.runAnalysis()

    def modelPathByVoxel(self, voxel_idx):

        model_filename = self.input_file_name_for_voxel(voxel_idx)

        model_input_file_path = os.path.join(self.batchOutputDir, model_filename)

        return model_input_file_path

    def runAnalysisWithCiftiProcessing(self, testing_only_limit_to_n_rows):
        start_time = time.time()

        self.input.prepare_with_cifti("PATH_HCP", self.output_path, testing_only_limit_to_n_rows)

        time2 = time.time()
        logging.info("Time to read cifti data and prepare csvs with cifti data: %f seconds" % (time2 - start_time))

        self.generateInputModelsWithVoxel(testing_only_limit_to_n_rows)

        time3 = time.time()
        logging.info("Time to prepare prepare mplus model files %f seconds" % (time3 - time2))

        self.runAllVoxelBasedModels(testing_only_limit_to_n_rows)

        time4 = time.time()

        logging.info("Time to run mplus model files %f seconds" % (time4 - time3))

        # load a standard baseline cifti that we will overwrite with our computed data
        output_cifti = self.base_cifti_for_output()

        path_template_for_data_including_voxel = self.base_output_path + ".voxel%s.inp.out"

        # note this code is a little confusing, there are updates happening to the cift objects
        # while it is return a data frame that contains all the aggregated values
        aggregated_results = self.model.aggregate_results(self.input, path_template_for_data_including_voxel,
                                                          ["Akaike (AIC)"],
                                                          [output_cifti],
                                                          testing_only_limit_to_n_rows=testing_only_limit_to_n_rows)
        time5 = time.time()

        logging.info("Time to aggregate mplus results %f seconds" % (time5 - time4))

        cifti_output_path = self.output_path + ".out.dscalar.nii"
        output_cifti.save(cifti_output_path)
        time6 = time.time()
        logging.info("Time to run generate new cifti %f seconds" % (time6 - time5))

        aggregated_results.to_csv(cifti_output_path + ".raw.csv", header=True, index=False)
        self._cifti_output_path = cifti_output_path

        logging.info("TOTAL TIME %f seconds" % (time.time() - start_time))
        return "Ran vectorized model."

    def generateInputModelsWithVoxel(self, testing_only_limit_to_n_rows):
        for i in range(self.input.cifti_vector_size):

            model_input_file_path = self.modelPathByVoxel(i)

            self.model.datafile = self.data_filename + "." + str(i) + ".csv"

            self.updateGeneratedMPlusInputFile(model_input_file_path, add_voxel_column_name="VOXEL")

            if testing_only_limit_to_n_rows > 0 and i >= testing_only_limit_to_n_rows - 1:
                break

    def runAllVoxelBasedModels(self, testing_only_limit_to_n_rows):
        num_threads = self.config.getOptional("mplus_threads", 4)
        if testing_only_limit_to_n_rows > 0:
            n = testing_only_limit_to_n_rows
        else:
            n = self.input.cifti_vector_size

        sets_of_model_paths = np.array_split(list(range(n)), num_threads)

        threads = []

        self.mplus_exec_counterQueue = queue.Queue()
        self.mplus_exec_count = 0
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
                self.mplus_exec_count = count
                if count > 0 and count % 2 == 0:
                    seconds = time.time() - self.mplus_exec_start_time
                    rate = seconds / count
                    logging.info("Mplus Models executed: %i in %f seconds (%f sec/model)" % (
                    self.mplus_exec_count, seconds, rate))
                self.mplus_exec_counterQueue.task_done()
        except:
            logging.info("queue monitor complete (empty queue)")

    def runMplusForSetOfVoxels(self, set_of_voxels):

        for i in set_of_voxels:
            model_input_file_path = self.modelPathByVoxel(i)

            result = self.runMplus(model_input_file_path)

            self.mplus_exec_counterQueue.put(i)

            # todo monitor these for errors
            # ok = self.evalMplusStdOut(result)

    def evalMplusStdOut(self, result):
        # todo monitor these for errors
        something_bad_happened = False
        if something_bad_happened:
            raise ValueError("Something bad is in the mplus output")

        return True

    def runAnalysis(self):
        model_filename = "input.inp"
        model_input_file_path = os.path.join(self.batchOutputDir, model_filename)
        model_output_file_path = model_input_file_path + ".out"
        self.model.datafile = self.data_filename
        self.updateGeneratedMPlusInputFile(model_input_file_path)
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

    def runMplus(self, model_input_file_path):
        # launch mplus

        # todo safety check this in case of rogue yml input!

        cmd = self.config._data["MPlus_command"] + " " + model_input_file_path

        result = subprocess.run([self.config._data["MPlus_command"],
                                 model_input_file_path,
                                 model_input_file_path + ".out"], stdout=subprocess.PIPE)

        return result

    def base_cifti_for_output(self):
        output_cifti = Cifti(self.config._data["Base_cifti_for_output"])

        output_cifti.nullify()

        return output_cifti
