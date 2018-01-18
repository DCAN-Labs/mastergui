import re
import time
import logging
import os
import json
import models.mplus_analysis
#import models.palm_analysis
from models.cifti import *
from models.cifti_matrix import *


class Analysis():
    """SuperClass for Specific analyses such as Mplus, Palm, etc

    Standardizes treatment of config file information and structuring of output directories"""

    def __init__(self,config, module_name, filename = ""):

        #this will be used when saving/loading files to indicate which kind of analysis it is
        self.module_name = module_name
        self.config = config
        self.required_config_keys = []
        self.filename = filename
        self.execution_history = []
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

        save_data = {"title":"mytitle", "module":self.module_name, "version":0.1, "execution_history":self.execution_history}

        if hasattr(self,'template'):
            template = self.template
            if hasattr(template,'data'):
                save_data['template'] = self.template.data

        self.module_specific_save_data(save_data)

        with open(filename, "w") as f:
            json.dump(save_data, f)

    def module_specific_save_data(self, save_data):
        """override in subclasses, add any attributes to save_data dictionary that should be included in the saved json file"""
        print("override in subclasses, add any attributes to save_data dictionary that should be included in the saved json file")

    def add_execution_history(self, output_dir, limit_by_voxel, limit_by_row):
        history_record = {"output_dir":output_dir, "limit_by_voxel":limit_by_voxel, "limit_by_row":limit_by_row}
        self.execution_history.append(history_record)

    def base_cifti_for_output(self):
        output_cifti = Cifti(self.config._data["Base_cifti_for_output"])

        output_cifti.nullify()

        return output_cifti

    def generate_ciftis_from_csv(self, csv_path):
        data = pd.read_csv(csv_path)
        self.generate_ciftis_from_dataframe(data)

    def generate_ciftis_from_dataframe(self, data):

        for c in data.columns:
            cifti = self.base_cifti_for_output()
            cifti.setVector(data[c])
            cifti_output_path = os.path.join(self.output_path ,c,".dscalar.nii")
            cifti.save(cifti_output_path)



    @classmethod
    def load(self, filename, config):

        with open(filename,'r') as f:
            load_data = json.load(f)

        module_name = load_data["module"]

        if module_name == "mplus":
            a = models.mplus_analysis.MplusAnalysis(config, filename, load_data)
        elif module_name == "palm":
            a = models.palm_analysis.PalmAnalysis(config, filename, load_data)
        elif module_name == "fconnanova":
            a = models.fconnanova_analysis.FconnanovaAnalysis(config, filename, load_data)
        else:
            raise ValueError("unknown module name: %s " % module_name)

        if "execution_history" in load_data:
            exec_hist = load_data["execution_history"]
            if len(exec_hist) == 0:  #if the subclass hadn't already processed the load history add it in its raw form
                a.execution_history = exec_hist
        return a
