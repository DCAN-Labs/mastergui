import datetime
import os
import subprocess
from models.cifti import *


class MplusAnalysis:
    def __init__(self, config):
        self.config = config

    def updateGeneratedMPlusInputFile(self, save_to_path=""):
        columns = self.input.columnnames()

        self.model.set_column_names(columns)

        #        generated_mplus_model = self.model.to_string()
        #        self.generatedModelViewer.setText(generated_mplus_model)

        if len(save_to_path) > 0:
            with open(save_to_path, "w") as f:
                f.write(self.model.to_string())

    @property
    def filename_prefix(self):
        # make data file with non alphanumeric characters replaced with _
        return self.model.title_for_filename

    @property
    def base_output_path(self):
        return os.path.join(self.config._data.get("output_dir", ""), self.filename_prefix)

    @property
    def data_filename(self):
        return self.filename_prefix + ".csv"

    @property
    def output_path(self):
        return os.path.join(self.config._data.get("output_dir", ""), self.data_filename)

    @property
    def output_dir(self):
        return self.config._data.get("output_dir", "")

    def input_file_name_for_voxel(self, voxel_index):
        return "%s.voxel%s.inp" % (self.filename_prefix, str(voxel_index))

    def go(self, model, title, input, missing_tokens_list, testing_only_limit_to_n_rows=3, needsCiftiProcessing=True):

        if len(title) == 0:
            title = "Untitled"

        title = title + str(datetime.datetime.now()).replace(" ", ".").replace(":", ".")

        self.model = model

        self.model.title = title

        self.input = input

        self.input.save_cleaned_data(self.output_path, missing_tokens_list)

        self.needCiftiProcessing = needsCiftiProcessing

        if self.needCiftiProcessing:
            return self.runAnalysisWithCiftiProcessing(testing_only_limit_to_n_rows)
        else:
            return self.runAnalysis()

    def runAnalysisWithCiftiProcessing(self, testing_only_limit_to_n_rows):

        self.input.prepare_with_cifti("PATH_HCP", self.output_path, testing_only_limit_to_n_rows)
        for i in range(self.input.cifti_vector_size):
            model_filename = self.input_file_name_for_voxel(i)

            model_input_file_path = os.path.join(self.output_dir, model_filename)

            self.model.datafile = self.data_filename + "." + str(i) + ".csv"

            self.updateGeneratedMPlusInputFile(model_input_file_path)

            result = self.runMplus(model_input_file_path)

            # todo monitor these for errors
            ok = self.evalMplusStdOut(result)

            if testing_only_limit_to_n_rows > 0 and i > testing_only_limit_to_n_rows:
                break

        # load a standard baseline cifti that we will overwrite with our computed data
        output_cifti = self.base_cifti_for_output()
        self.model.aggregate_results_to_cifti(self.input, self.base_output_path, ["Akaike (AIC)"], [output_cifti])
        cifti_output_path = self.output_path + ".out.dscalar.nii"
        output_cifti.save(cifti_output_path)
        self._cifti_output_path = cifti_output_path
        return "Ran vectorized model."

    def evalMplusStdOut(self, result):
        # todo monitor these for errors
        something_bad_happened = False
        if something_bad_happened:
            raise ValueError("Something bad is in the mplus output")

        return True

    def runAnalysis(self):
        model_filename = self.model.title_for_filename + ".inp"
        model_input_file_path = os.path.join(self.config._data["output_dir"], model_filename)
        model_output_file_path = model_input_file_path + ".out"
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
