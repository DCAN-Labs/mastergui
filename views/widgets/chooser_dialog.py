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
from views.widgets.chooser import *


class ChooserDialog(QDialog):
    def __init__(self, data):
        super(ChooserDialog, self).__init__()
        self.data = data
        self.initUI()

    #        self.loadColumns()

    def initUI(self):
        layout = QVBoxLayout()

        self.chooser = Chooser(self.data, checkable=True)
        # False:True
        #        layout.addWidget(radio_group)
        layout.addWidget(self.chooser)

        addButton("OK", layout, self.on_click_ok)
        addButton("Cancel", layout, self.on_click_ok)

        self.setLayout(layout)

    def on_click_ok(self):
        print("ok")
        # todo implement
        self.close()

    def on_click_cancel(self):
        self.close()


        # def loadColumns(self):

        # self.addColumnNamesToListView(self.columnListWidget, self.data)

    def addColumnNamesToListView(self, listView, columnNames):
        model = listView.model()

        model.clear()

        for col in columnNames:
            item = QStandardItem(col)
            # check = Qt.Checked if 1 == 1 else Qt.Unchecked
            # item.setCheckState(check)
            model.appendRow(item)

    def showModally(self):
        self.setWindowModality(Qt.WindowModal)
        self.show()
        self.exec_()

    def selectedRow(self):
        return self.chooser.selectedRow()

    # @ Darrick added this method
    def getItems(self):
        return self.chooser.getItems()
