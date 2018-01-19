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


class ColumnChooserDropDown(QComboBox):
    def __init__(self, input_spreadsheet = None, initial_value = ""):
        super(ColumnChooserDropDown, self).__init__()
        self.input_spreadsheet = input_spreadsheet
        self.loadColumns()
        self.setValueToColumn(initial_value)
        self.setMinimumWidth(200)

    def loadColumns(self):

        columns = [""]
        if self.input_spreadsheet is not None:
            columns += list(self.input_spreadsheet.data().columns)

        for col in columns:
            self.addItem(col)

    def setValueToColumn(self, column_name):
        index = self.findText(column_name, Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)

    def updateInputSpreadsheet(self, input):
        self.input_spreadsheet = input
        self.loadColumns()
