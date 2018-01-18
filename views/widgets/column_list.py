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


class ColumnList(QWidget):
    def __init__(self, caption):
        super(ColumnList, self).__init__()
        self.caption = caption
        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()

        layout.addWidget(createBoldLabel(self.caption))
        model = QStandardItemModel()

        list = QListView()
        list.setModel(model)
        self.columnListWidget = list


        layout.addWidget(list)

        self.setLayout(layout)


        buttonLayout = QHBoxLayout()
        self.btnAdd = addButton("+", buttonLayout, self.on_click_add)

        self.btnRemove = addButton("-", buttonLayout, self.on_click_remove)

        buttonLayout.addWidget(self.btnAdd)
        buttonLayout.addWidget(self.btnRemove)
        gb = QGroupBox()
        gb.setLayout(buttonLayout)
        layout.addWidget(gb)

    def setAddClickHandler(self, handler):
        self.btnAdd.clicked.connect(handler)

    def setRemoveClickHandler(self, handler):
        self.btnRemove.clicked.connect(handler)

    def on_click_add(self):
        print("add")

    def on_click_remove(self):
        print("remove")

    def loadValues(self, values):

        self.refreshList(values)

    def refreshList(self, columnNames):

        model = self.columnListWidget.model()

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
        if len(idx)>0:
            return m.itemFromIndex(idx[0]).text()

        return None