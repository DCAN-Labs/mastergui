from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
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


class Chooser(QWidget):
    def __init__(self, data, filter_labels=[], default_value=None, checkable=True):
        super(Chooser, self).__init__()
        self.checkable = checkable
        self.default_value = default_value
        self.data = data
        self.filter_labels = filter_labels
        self.initUI()
        self.loadColumns()
        self.items = []

    def initUI(self):

        layout = QVBoxLayout()

        model = QStandardItemModel()
        model.itemChanged.connect(self.setItems)  # @ Darrick final changes

        list = QListView()
        list.setModel(model)
        self.columnListWidget = list

        if len(self.filter_labels) > 0:
            self.filter = self.createFilter()

            layout.addWidget(self.filter)

        layout.addWidget(list)

        self.setLayout(layout)

    def createFilter(self):

        combo = QComboBox()
        for label in self.filter_labels:
            combo.addItem(label)
        combo.currentIndexChanged.connect(self.on_filter_changed)
        return combo

    def on_filter_changed(self):
        # todo
        print('change column list')

    def on_pattern_btn_clicked(self, a):
        print(a)
        # todo change set of columns that is displayed

    def loadColumns(self):

        self.addColumnNamesToListView(self.columnListWidget, self.data)
        self.set_default()

    def set_default(self):
        if self.default_value is not None:
            m = self.columnListWidget.model()

    def addColumnNamesToListView(self, listView, columnNames):

        model = listView.model()

        model.clear()

        for col in columnNames:
            item = QStandardItem(col)
            # check = Qt.Checked if 1 == 1 else Qt.Unchecked
            # item.setCheckState(check)
            if self.checkable:
                item.setCheckable(True)
            model.appendRow(item)

    def selectedRow(self):
        m = self.columnListWidget.model()
        idx = self.columnListWidget.selectedIndexes()
        if len(idx) > 0:
            return m.itemFromIndex(idx[0]).text()

        return None

    # @ Darrick added
    def setItems(self, item):
        if item.checkState() == Qt.Checked:
            self.items.append(item)
        if item.checkState() == Qt.Unchecked:
            self.items.remove(item)

    def getItems(self):
        return [i.text() for i in self.items]
