from models.paths import *
from models.config import *
import datetime
import os.path
import subprocess

class PostProcessing():
    def __init__(self, config):
        self.config = config

        available_postprocessing_options = config.data["analyzers"]["mplus"]["postprocessingoptions"]

        pp_commands = {}

        # load the available post procssing commands into a dictionary for convenient access
        for item in available_postprocessing_options:
            pp_commands[item["name"]] = item

        self.pp_commands = pp_commands

    def run(self, postprocessing_command_name, source_cifti_path, param_file_contents):

        command_desc = self.pp_commands[postprocessing_command_name]

        cmd = command_desc["command"]

        dir_of_cifti = os.path.split(source_cifti_path)[0]

        timestamp = str(datetime.datetime.now()).replace(" ","_")

        param_file_name = os.path.join(dir_of_cifti, "%s_%s_%s_params.bash" % (source_cifti_path, postprocessing_command_name, timestamp ))

        with open(param_file_name, "w") as f:
            f.write(param_file_contents)


        result = subprocess.run([cmd,
                                 param_file_name], stdout=subprocess.PIPE)

        return result

    def build_parameter_file(self, postprocessing_command_name, source_cifti_path):
        """reads the default parameter file for the postprocessing command and substitutes in the paths for the input and output cifti

        returns a string with the contents for the new param file
        """
        if postprocessing_command_name in self.pp_commands:
            options = self.pp_commands[postprocessing_command_name]

            default_options_path = options["param_filepath"]

            try:
                with open(default_options_path, "r") as f:
                    lines = f.readlines()

                #remove the lines from the default param file with "InputCifti=" and "OutputCifti=" as
                #those will be overwritten by MasterGUI

                lines = [line for line in lines if
                         line.strip().find("InputCIFTI=") == -1 and line.strip().find("OutputCIFTI=") == -1]
                lines.append("InputCIFTI=%s\n" % source_cifti_path)
                lines.append("OutputCIFTI=%s.%s.dscalar.nii\n" %  (source_cifti_path, postprocessing_command_name))

                return "".join(lines)
            except:
                raise Exception("error opening parameter file template for post processing module")
        else:
            raise Exception("No configuration information for post-procssing command %s is available.  " % postprocessing_command_name)