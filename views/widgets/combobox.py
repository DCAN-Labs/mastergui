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


class ComboBox(QComboBox):
    def __init__(self, data=[], initial_value="", on_change = None):
        super(ComboBox, self).__init__()
        self.data = data

        self.loadColumns()
        self.setValue(initial_value)
        if on_change:
            self.currentTextChanged.connect(on_change)
        #self.setMinimumWidth(200)

    def loadColumns(self):
        old_value = self.currentText()
        self.clear()


        for col in self.data:
            self.addItem(col)

        if len(old_value)>0:
            idx = self.findText(old_value)
            if idx >= 0:
                self.setCurrentIndex(idx)

    def setValue(self, column_name):
        index = self.findText(column_name, Qt.MatchFixedString)
        if index >= 0:
            self.setCurrentIndex(index)

    def update(self, data):
        self.data = data
        self.loadColumns()
