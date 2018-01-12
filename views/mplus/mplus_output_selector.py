from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import glob
import os
import numpy as np
from views.output_browser import *
from views import view_utilities
import sys

class MplusOutputSelector(OutputBrowserWidget):
    def __init__(self, parentAnalysisWidget):
        super(MplusOutputSelector, self).__init__()
        self.hidePatternSelector()
        self.patternWidget.setText("*.out")
        #self.fileViewer.setVisible(False)
        #self.exploreLayout.addWidget(self.listView,stretch = 5)

        #self.exploreLayout.removeWidget(self.)
        #self.layout().removeWidget(self.groupWidget)
        self.parentAnalysisWidget = parentAnalysisWidget
        view_utilities.addButton("Extract", self.layout(), self.extract)

    def initDetailUI(self, exploreLayout):
        self.createOutputSelector()
        exploreLayout.addWidget(self.selectableOutput, stretch=5)

    def createOutputSelector(self):

        self.selectableOutput = QListView()

        model = QStandardItemModel()

        self.selectableOutput.setModel(model)

    def on_row_changed(self, current, previous):

        path = os.path.join(self.output_dir, current.data())

        with open(path,'r') as f:
            contents = f.readlines()

        self.addValuesToList(self.selectableOutput, contents)
        #self.fileViewer.setText("".join(contents))

    def is_number(self, word):
        try:
            float(word)
            return True
        except:
            return False

    def isCheckable(self, line):
        if len(line) > len(line.lstrip()):
            words = line.strip().split(" ")
            #if the last value on the line is a number let it be checkable
            return self.is_number(words[-1])
        else:
            return False
    def addValuesToList(self, listView, lines):

        model = listView.model()

        model.clear()

        original_line_number = 0

        item_number = 0

        item_to_line_numbers = {}

        for line in lines:
            if len(line.strip())>0:
                item = QStandardItem(line)
                # check = Qt.Checked if 1 == 1 else Qt.Unchecked
                # item.setCheckState(check)
                if self.isCheckable(line):
                    item.setCheckable(True)
                item.setSizeHint(QSize(300,15))
                model.appendRow(item)
                item_to_line_numbers[item_number] = original_line_number
                item_number+=1

            original_line_number += 1

        self.item_to_line_numbers = item_to_line_numbers

    def selectedOutputRows(self):

        m = self.selectableOutput.model()

        items = []
        for i in range(m.rowCount()):
            item = m.item(i)
            if item.checkState() == Qt.Checked:
                print("m here")
                line_number = self.item_to_line_numbers[i]
                line = item.text()
                name = line.strip().split(" ")[0]
                items.append((line_number,line, name))
        return items

    def extract(self):
        try:
            selected = self.selectedOutputRows()

            path_template_for_data_including_voxel = os.path.join(self.output_dir,"input.voxel%s.inp.out")

            input =  self.parentAnalysisWidget.input
            analysis = self.parentAnalysisWidget.analysis


            if analysis.limit_by_voxel>0:
                cifti_vector_size = analysis.limit_by_voxel
            else:
                if hasattr(input,"cifti_vector_size"):
                    cifti_vector_size = input.cifti_vector_size
                else:
                    cifti_vector_size = 0

            results = self.parentAnalysisWidget.model.aggregate_results_by_line_number(cifti_vector_size, path_template_for_data_including_voxel, selected)
            results.to_csv(os.path.join(self.output_dir,"extracted.csv"), index=False)


            self.parentAnalysisWidget.analysis.generate_ciftis_from_dataframe(results)

        except:
            self.parentAnalysisWidget.alert(sys.exc_info()[1])
            return