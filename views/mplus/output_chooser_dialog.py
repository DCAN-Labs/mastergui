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
import os
import threading
import traceback
import time
from views.view_utilities import *
from views.widgets.chooser_dialog import *
from views.widgets.chooser import *
from models.mplus.output_parser import *

# from views.mplus import *
import views.mplus.output_chooser_dialog


class OutputChooserDialog(ChooserDialog):
    def __init__(self, path_to_mplus_output):
        self.data = []
        self.readOutputFile(path_to_mplus_output)
        super(OutputChooserDialog, self).__init__(self.data)
        self.setFixedWidth(600)
        self.selection = None
        self.showModally()

    def readOutputFile(self, path_to_mplus_output):
        try:
            mp = MplusOutput(path_to_mplus_output)
            self.data = sorted(mp.data.keys())
        except:
            util.alert("Error opening MPlus Output file %s" % path_to_mplus_output)

    def on_click_ok(self):
        self.selection = self.chooser.selectedRow()
        # todo implement
        self.close()
