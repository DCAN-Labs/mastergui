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
from views.widgets.column_chooser import *
from views.widgets.column_chooser_dialog import *


class VoxelizerDialog(ColumnChooserDialog):
    def __init__(self, input_spreadsheet):
        super(VoxelizerDialog, self).__init__(input_spreadsheet, checkable = False)
        self.initMoreUI()

    def initMoreUI(self):

        form = QFormLayout()
        self.new_name_widget = QLineEdit()

        form.addRow(createBoldLabel("Name for the Voxel Variable:"), self.new_name_widget)

        formWidget = QWidget()
        formWidget.setLayout(form)
        self.layout().insertWidget(1, formWidget)
        self.showModally()

    def mapping(self):
        from_col = self.selectedRow()
        if not from_col is None:

            to_col = self.new_name_widget.text()

            if len(to_col) > 0:
                return (from_col, to_col)

        return None

    def validate(self):
        """overriding the default method to require that the user entered a name for their voxel"""
        t = self.new_name_widget.text()
        if len(t)>0:
            if t in self.input_spreadsheet.columnnames():
                util.alert("'%s' is a name of a column in the existing data, please provide a different unique name" % t)
            else:
                return True
        else:
            util.alert("Please provide a unique name for the voxel data.")

        return False

    def showModally(self):
        self.setWindowModality(Qt.WindowModal)
        self.show()
        self.exec_()
