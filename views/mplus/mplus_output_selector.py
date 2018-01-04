from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import glob
import os
import numpy as np
from views.output_browser import *

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
        self.repaint()

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
