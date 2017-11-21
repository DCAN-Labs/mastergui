import datetime
import os
import subprocess


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

    def go(self, model, title, input, missing_tokens_list, testing_only_limit_to_n_rows=3):

        if len(title) == 0:
            title = "Untitled"

        title = title + str(datetime.datetime.now()).replace(" ", ".").replace(":", ".")

        self.model = model

        self.model.title = title

        self.input = input

        # make data file with characters replaced
        filename_prefix = self.model.title_for_filename

        data_filename = filename_prefix + ".csv"

        base_output_path = os.path.join(self.config._data.get("output_dir", ""), filename_prefix)
        output_path = os.path.join(self.config._data.get("output_dir", ""), data_filename)

        self.input.save_cleaned_data(output_path, missing_tokens_list)

        self.input.prepare_with_cifti("PATH_HCP", output_path, testing_only_limit_to_n_rows)

        for i in range(self.input.cifti_vector_size):
            model_filename = self.model.title_for_filename + ".voxel" + str(i) + ".inp"

            model_input_file_path = os.path.join(self.config._data["output_dir"], model_filename)
            self.model.datafile = data_filename + "." + str(i) + ".csv"
            model_output_file_path = model_input_file_path + ".out"
            self.updateGeneratedMPlusInputFile(model_input_file_path)

            # launch mplus
            cmd = self.config._data["MPlus_command"] + " " + model_input_file_path

            result = subprocess.run([self.config._data["MPlus_command"],
                                     model_input_file_path,
                                     model_output_file_path], stdout=subprocess.PIPE)

            if testing_only_limit_to_n_rows > 0 and i > testing_only_limit_to_n_rows:
                break

        # hack
        # temp
        # todo
        # just grabbing an arbitrary cifti from the input to use as the basis for making a new cifti
        all_ciftis = self.input.ciftiSet.ciftis

        output_cifti = all_ciftis[next(iter(all_ciftis))]

        self.model.aggregate_results_to_cifti(self.input, base_output_path, ["Akaike (AIC)"], [output_cifti])

        cifti_output_path = output_path + ".out.dscalar.nii"

        output_cifti.randomize()

        output_cifti.save(cifti_output_path)

        model_filename = self.model.title_for_filename + ".inp"

        model_input_file_path = os.path.join(self.config._data["output_dir"], model_filename)

        model_output_file_path = model_input_file_path + ".out"

        self.updateGeneratedMPlusInputFile(model_input_file_path)

        # todo safety check this in case of rogue yml input!
        # launch mplus
        cmd = self.config._data["MPlus_command"] + " " + model_input_file_path

        result = subprocess.run([self.config._data["MPlus_command"],
                                 model_input_file_path,
                                 model_output_file_path], stdout=subprocess.PIPE)

        self.mplus_stdout = str(result.stdout, 'utf-8')

        with open(model_output_file_path, "r") as f:
            mplus_output_contents = f.read()

        self.cifti_output_path = cifti_output_path

        return mplus_output_contents
