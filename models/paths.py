import os
import re
import datetime

BATCHES_DIRNAME = "batches"
INPUTS_DIRNAME = "inputs"
OUTPUTS_DIRNAME = "outputs"
CIFITS_DIRNAME = "ciftis"

class Paths():
    def __init__(self, analysis_root_output_dir):
        self.root = analysis_root_output_dir
        self.current_batch_name = ""

    @property
    def batches_dir(self):
        return os.path.join(self.root,BATCHES_DIRNAME)

    def batches(self):

        p = self.batches_dir

        if os.path.exists(p):
            return [d for d in os.listdir(p) if os.path.isdir(os.path.join(p,d))]
        else:
            return []

    def confirm_batches_dir(self):
        p = self.batches_dir

        if os.path.exists(p):
            return True
        else:
            try:
                os.mkdir(p)
                return True
            except Exception as e:
                raise ValueError("Unable to create required 'batches' subdirectory in your choosen output directory %s for this analysis. Check your permissions." % s)

    #@property
    # def batch_output_dir(self):
    #     return os.path.join(self.batches_dir, self.current_batch_name,OUTPUTS_DIRNAME)
    #
    # @property
    # def batch_inputs_dir(self):
    #     return os.path.join(self.batches_dir, self.current_batch_name, INPUTS_DIRNAME)
    #
    # @property
    # def batch_ciftis_dir(self):
    #     return os.path.join(self.batches_dir, self.current_batch_name, CIFTIS_DIRNAME)

    @property
    def current_batch_path(self):
        return os.path.join(self.batches_dir,self.current_batch_name)

    def path_for_batch_name(self, batch_name):
        return os.path.join(self.batches_dir,batch_name)

    def create_new_batch(self):
        if self.confirm_batches_dir():
            new_batch_dir_name = str(datetime.datetime.now()).replace(" ", ".").replace(":", ".")
            self.current_batch_name = new_batch_dir_name
            os.mkdir(self.current_batch_path)
            if len(OUTPUTS_DIRNAME) > 0:
                os.mkdir(self.batch_outputs_path())
            if len(INPUTS_DIRNAME) > 0:
                os.mkdir(self.batch_inputs_path())
            if len(CIFITS_DIRNAME) > 0:
                os.mkdir(self.batch_cifits_path())

    def batch_inputs_path(self, filename = ""):
        """
                Uses the settings for this analysis, standard folder structure, and current batch title to
                construct the path for inputs to the underlying analysis program  to go

                :param filename:  if a filename is provided it will provide the path to that specific file in the same directory context
                :return: the full path to the folder {AnalysisRoot}/Batches/{CurrentBatch}/{OuputsSubDirIfAny}
                """
        return os.path.join(self.current_batch_path, INPUTS_DIRNAME, filename)

    def batch_outputs_path(self, filename = ""):
        """
        Uses the settings for this analysis, standard folder structure, and current batch title to
        construct the path for outputs that the underlying analysis program generates to go

        :param filename:  if a filename is provided it will provide the path to that specific file in the same directory context
        :return: the full path to the folder {AnalysisRoot}/Batches/{CurrentBatch}/{OuputsSubDirIfAny}
        """
        return os.path.join(self.current_batch_path, OUTPUTS_DIRNAME, filename)

    def batch_cifits_path(self, filename = ""):
        return os.path.join(self.current_batch_path, CIFITS_DIRNAME, filename)