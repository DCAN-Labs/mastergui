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


class ColumnChooser(QWidget):
    def __init__(self, parentAnalysisWindow = None,data_preview_widget):
        super(ColumnChooser, self).__init__()

        self.data_preview = data_preview_widget

