from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from views.analysis_window_base import *
from views.data_preview_widget import *
from views.output_browser import *
from views.mplus.mplus_output_selector import *
import views.workbench_launcher
import models
import datetime
import sys
import threading
import traceback
import time
from views.view_utilities import *

class ColumnChooserDialog(QDialog):
    def __init__(self, input_spreadsheet ):
        super(ColumnChooserDialog, self).__init__()
        self.input_spreadsheet = input_spreadsheet
        self.initUI()
        self.loadColumns()

    def initUI(self):

        layout = QVBoxLayout()

        chooser = ColumnChooser(self.input_spreadsheet)
        layout.addWidget(radio_group)
        layout.addWidget(chooser)

        addButton("OK",layout, self.on_click_ok)
        addButton("Cancel", layout, self.on_click_ok)

        self.setLayout(layout)

    def on_click_ok(self):
        print("ok")
        #todo implement
        self.close()
    def on_click_cancel(self):
        self.close()
    def createRadioButtons(self):
        labels = ["All", "Categorical", "Scalar"]
        #self.patterns = ["*.csv", "*.inp", "*.out"]
        group = QButtonGroup()
        groupWidget = QWidget()
        layout = QHBoxLayout()

        idx = 0
        for label in labels:
            btn = QRadioButton(label)

            group.addButton(btn, idx)
            layout.addWidget(btn)
            idx += 1

        groupWidget.setLayout(layout)
        groupWidget.setFixedWidth(400)
        group.buttonClicked.connect(self.on_pattern_btn_clicked)
        self.patternButtonGroup = group
        self.groupWidget = groupWidget

        return groupWidget

    def on_pattern_btn_clicked(self,a):
        print(a)
        #todo change set of columns that is displayed


    def loadColumns(self):


        columns = list(self.input_spreadsheet.data().columns)
        self.addColumnNamesToListView(self.columnListWidget,columns)


    def addColumnNamesToListView(self, listView, columnNames):

            model = listView.model()

            model.clear()

            for col in columnNames:
                item = QStandardItem(col)
                # check = Qt.Checked if 1 == 1 else Qt.Unchecked
                # item.setCheckState(check)
                item.setCheckable(True)
                model.appendRow(item)

