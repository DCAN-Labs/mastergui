from views.widgets.column_list import *
from views.mplus.mplus_postprocessing_options_editor import *
from views.view_utilities import *
from models.post_processing import *


class MPlusPostProcessingOptions(ColumnList):
    def __init__(self, config, callback_to_find_ciftipath):
        super(MPlusPostProcessingOptions, self).__init__("Post-Processing Options")
        self.config = config

        available_postprocessing_options = []
        try:
            available_postprocessing_options = config.data["analyzers"]["mplus"]["postprocessingoptions"]
        except:
            print("no post processing options found")

        option_names = [i["name"] for i in available_postprocessing_options]
        self.loadValues(option_names)

        self.setAddClickHandler(self.run_postprocessing)
        self.callback_to_find_ciftipath = callback_to_find_ciftipath

    def run_postprocessing(self):
        # need to build the options file to contain the proper set of values.
        # so for the given post-processing file we will need to know what paths to set, popup a form to let them see it.

        cifti_path = self.callback_to_find_ciftipath()

        if len(cifti_path) == 0:
            alert("Please select a cifti first and try again.")
            return

        selectedOne = self.selectedRow()
        pp_name = selectedOne

        popup = MPlusPostProcessingOptionsEditor(self.config, pp_name, cifti_path)
        popup.showModally()

        if not popup.cancelled:
            value = popup.text.toPlainText()

            pp = PostProcessing(self.config)
            pp.run(pp_name, cifti_path, value)
            # todo save to file and execute command.
            print(value)
