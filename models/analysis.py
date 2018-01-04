import re
import time
import logging
import os
import json
import models.mplus_analysis
#import models.palm_analysis


class Analysis():
    """SuperClass for Specific analyses such as Mplus, Palm, etc

    Standardizes treatment of config file information and structuring of output directories"""

    def __init__(self,config, module_name, filename = ""):

        #this will be used when saving/loading files to indicate which kind of analysis it is
        self.module_name = module_name
        self.config = config
        self.required_config_keys = []
        self.filename = filename
        self.cancelling = False

    @property
    def filename_prefix(self):
        # make data file with non alphanumeric characters replaced with _
        return "input"  # self.model.title_for_filename

    @property
    def base_output_path(self):
        return os.path.join(self.batchOutputDir, self.filename_prefix)


    @property
    def output_dir(self):
        return self.config._data.get("output_dir", "")

    def missingRequiredConfigKeys(self):
        missing_keys = [k for k in self.required_config_keys if not k in self.config._data]
        return missing_keys


    def setBatchTitle(self, raw_title):
        self.batchTitle = re.sub('[^0-9a-zA-Z]+', '_', self.dir_name_for_title(raw_title))


    def progressMessage(self, txt):

        logging.info(txt)
        if self.progress_callback is not None:
            self.progress_callback.emit(txt)

    def save(self, filename):

        save_data = {"title":"mytitle", "module":self.module_name, "version":0.1}

        self.module_specific_save_data(save_data)

        with open(filename, "w") as f:
            json.dump(save_data, f)

    def module_specific_save_data(self, save_data):
        """override in subclasses, add any attributes to save_data dictionary that should be included in the saved json file"""
        print("override in subclasses, add any attributes to save_data dictionary that should be included in the saved json file")

    @classmethod
    def load(self, filename, config):

        with open(filename,'r') as f:
            load_data = json.load(f)

        module_name = load_data["module"]

        if module_name == "mplus":
            a = models.mplus_analysis.MplusAnalysis(config, filename)
        elif module_name == "palm":
            a = models.palm_analysis.PalmAnalysis(config, filename)
        elif module_name == "fconnanova":
            a = models.fconnanova_analysis.FconnanovaAnalysis(config, filename)
        else:
            raise ValueError("unknown module name: %s " % module_name)
        return a
