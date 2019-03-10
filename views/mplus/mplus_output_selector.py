from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import glob
import os
import numpy as np
from views.output_browser import *
from views import view_utilities
from views.mplus.output_chooser_dialog import *
from views.mplus.mplus_postprocessing_options import *
from views.widgets import *

import sys

output_radio_button_index = 1


class MplusOutputSelector(OutputBrowserWidget):
    def __init__(self, parentAnalysisWidget):
        super(MplusOutputSelector, self).__init__(parentAnalysisWidget)

        self.patternWidget.setText("outputs/*.*")
        self.last_selected_pattern_id = output_radio_button_index

        self.parentAnalysisWidget = parentAnalysisWidget
        view_utilities.addButton("Extract", self.groupWidget.layout(), self.on_click_extract)
        view_utilities.addButton("Choose Parameters", self.groupWidget.layout(), self.on_click_chooseparameters)

    def initDetailUISpecific(self, exploreLayout):
        self.createOutputSelector()
        self.selectableOutput.setVisible(False)
        exploreLayout.addWidget(self.selectableOutput, stretch=5)

        # todo planned UI refactor to move these output parameter and post processing options to the Output tab
        #     self.outputParameterChoiceList = ColumnList("Output Parameters",
        #                                                 self.on_click_add_output_parameter,
        #                                                 self.on_click_remove_output_parameter,
        #                                                 checkable=False)
        #     self.outputParameterChoiceList.setFixedHeight(150)

        #     self.addWidget(self.outputParameterChoiceList)

        self.postProcessingOptions = MPlusPostProcessingOptions(self.parentAnalysisWidget.config,
                                                                self.get_selected_file_path)
        self.postProcessingOptions.setVisible(False)  # this is only shown when Ciftis are being shown
        exploreLayout.addWidget(self.postProcessingOptions)

    def get_selected_file_path(self):
        if hasattr(self, 'last_selected_path'):
            return self.last_selected_path
        else:
            return ""

    def createOutputSelector(self):

        self.selectableOutput = QListView()

        model = QStandardItemModel()

        self.selectableOutput.setModel(model)

    def on_file_row_changed(self, current, previous):

        if self.last_selected_pattern_id == output_radio_button_index:

            path = os.path.join(self.selected_file_context, current.data())

            with open(path, 'r') as f:
                contents = f.readlines()
            self.last_selected_output_file_path = path

            self.addValuesToList(self.selectableOutput, contents)
            # self.fileViewer.setText("".join(contents))
        else:
            super(MplusOutputSelector, self).on_file_row_changed(current, previous)

    def is_number(self, word):
        try:
            float(word)
            return True
        except:
            return False

    def addValuesToList(self, listView, lines):

        model = listView.model()

        model.clear()

        original_line_number = 0

        item_number = 0

        item_to_line_numbers = {}

        for line in lines:
            if len(line.strip()) > 0:
                item = QStandardItem(line)

                item.setSizeHint(QSize(300, 15))
                model.appendRow(item)
                item_to_line_numbers[item_number] = original_line_number
                item_number += 1

            original_line_number += 1

        self.item_to_line_numbers = item_to_line_numbers

    def on_pattern_btn_clicked(self, i):

        selected_id = i.group().checkedId()
        self.last_selected_pattern_id = selected_id
        pattern = self.patterns[selected_id]
        self.patternWidget.setText(pattern)

        # some commands only make sense when ciftis are available
        show_cifti_options = selected_id == cifti_radio_button_index
        self.ciftiButtion.setVisible(show_cifti_options)
        self.postProcessingOptions.setVisible(show_cifti_options)

        if selected_id == cifti_radio_button_index:
            if self.fileViewer.isVisible():
                self.fileViewer.setVisible(False)
            if self.selectableOutput.isVisible():
                self.selectableOutput.setVisible(False)
        elif selected_id == output_radio_button_index:
            self.fileViewer.setVisible(False)
            self.selectableOutput.setVisible(True)
        else:
            if self.selectableOutput.isVisible():
                self.selectableOutput.setVisible(False)

            if not self.fileViewer.isVisible():
                self.fileViewer.setVisible(True)

        # self.fileViewer.setVisible(selected_id != cifti_radio_button_index)

        self.on_click_refresh()

    def on_click_extract(self):
        self.extract(True)
        util.alert("Extraction complete.")

    def on_click_chooseparameters(self):

        if hasattr(self, 'last_selected_output_file_path'):
            c = OutputChooserDialog(self.last_selected_output_file_path)
            if c.selection:
                # @ Darrick: Maybe this shouldn't be here (isinstance)
                if isinstance(c.selection, list):
                    for i in c.selection:
                        # @ Darrick test if we can take out checkable
                        print(type(i), i)
                        i.setCheckable(False)
                        self.parentAnalysisWidget.addOutputParameter(i)
                else:
                    self.parentAnalysisWidget.addOutputParameter(c.selection)

    @property
    def analysis(self):
        return self.parentAnalysisWidget.analysis

    def extract(self, use_currently_viewed_batch=False):
        try:
            analysis = self.analysis

            input = self.parentAnalysisWidget.input

            if analysis.limit_by_voxel > 0:
                cifti_vector_size = analysis.limit_by_voxel
            else:
                if hasattr(input, "cifti_vector_size"):
                    cifti_vector_size = input.cifti_vector_size
                else:
                    cifti_vector_size = 0

            if use_currently_viewed_batch:
                results = analysis.aggregate_results(batch_path=self.selected_batch_path, n_elements=cifti_vector_size)
            else:
                results = analysis.aggregate_results(n_elements=cifti_vector_size)

            self.showextractionwarnings(analysis.outputset)

        except:
            self.parentAnalysisWidget.alert(sys.exc_info()[1])
            return

    def showextractionwarnings(self, outputset):

        msg = "\nExtraction Errors And Warnings\n\n"

        msg += "Mplus Outputs with Any Error: %d\n" % len(outputset.any_errors)
        if len(outputset.any_errors) > 0:
            msg += "\tExamples: %s\n" % str(outputset.any_errors[:10])

        msg += "\nWarnings:\n"
        warning_counts = outputset.warning_counts

        for k, v in warning_counts.items():
            msg += "%d instances of %s\n" % (v, k)

        msg += "Counts of Missing Keys:\n"

        for k, v in outputset.not_found_counts.items():
            msg += "%d instances of %s\n not found\n" % (v, k)

        ntv = outputset.not_terminated_voxels
        if len(ntv) == 0:
            msg += "\nAll models 'terminated normally'\n"
        else:
            msg += "\n%d models did not terminate normally\n" % len(ntv)
            msg += "\tExamples: %s\n" % str(ntv[:10])

        tw = outputset.termination_warnings
        if len(tw) == 0:
            msg += "\nNo termination warnings among the models that 'terminated normally'\n"
        else:
            msg += "\nModel termination warnings among those that 'terminated normally':\n"
            for warn, ids in tw.items():
                msg += "\n\t%d examples of:\n\t%s\n" % (len(ids), warn)
                msg += "\n\tExamples: %s\n" % str(ids[:10])
        self.parentAnalysisWidget.appendTextToOutputDisplay(msg)
