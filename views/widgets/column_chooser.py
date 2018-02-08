from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from views.analysis_window_base import *
from views.widgets.data_preview_widget import *
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


class ColumnChooser(QWidget):
    def __init__(self, input_spreadsheet, default_value=None):
        super(ColumnChooser, self).__init__()
        self.default_value = default_value
        self.input_spreadsheet = input_spreadsheet
        self.initUI()
        self.loadColumns()

    def initUI(self):

        layout = QVBoxLayout()

        model = QStandardItemModel()

        list = QListView()
        list.setModel(model)
        self.columnListWidget = list

        self.filter = self.createFilter()

        layout.addWidget(self.filter)

        layout.addWidget(list)

        self.setLayout(layout)

    def createFilter(self):
        labels = ["All Columns", "Categorical Columns", "Scalar Columns"]
        combo = QComboBox()
        for label in labels:
            combo.addItem(label)
        combo.currentIndexChanged.connect(self.on_filter_changed)
        return combo

    def createRadioButtons(self):
        labels = ["All", "Categorical", "Scalar"]
        # self.patterns = ["*.csv", "*.inp", "*.out"]
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

    def on_filter_changed(self):
        # todo
        print('change column list')

    def on_pattern_btn_clicked(self, a):
        print(a)
        # todo change set of columns that is displayed

    def loadColumns(self):

        columns = list(self.input_spreadsheet.data().columns)
        self.addColumnNamesToListView(self.columnListWidget, columns)
        self.set_default()

    def set_default(self):
        if self.default_value is not None:
            m = self.columnListWidget.model()

            print("do something")

    def addColumnNamesToListView(self, listView, columnNames):

        model = listView.model()

        model.clear()

        for col in columnNames:
            item = QStandardItem(col)
            # check = Qt.Checked if 1 == 1 else Qt.Unchecked
            # item.setCheckState(check)
            item.setCheckable(True)
            model.appendRow(item)

    def selectedRow(self):
        m = self.columnListWidget.model()
        idx = self.columnListWidget.selectedIndexes()
        if len(idx) > 0:
            return m.itemFromIndex(idx[0]).text()

        return None

    def updateInputSpreadsheet(self, input):
        self.input_spreadsheet = input
        self.loadColumns()
