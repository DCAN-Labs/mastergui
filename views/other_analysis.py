from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from views.analysis_window_base import *
from views.data_preview_widget import *
import views.workbench_launcher
import models
import datetime
import sys
import threading
import traceback
import time


class OtherAnalysisWindow(AnalysisWindow):
    def __init__(self, config):
        self.default_missing_tokens_list = ["-888", "NA", "", "nan"]
        self.title = "Other Analysis (Demo)"
        self.analyzerName = "other"
        super(OtherAnalysisWindow, self).__init__(config)

    def onSelectTemplate(self, model_text):
        self.alert(
            "This Other Analysis is just a concept demonstration that has no actual functionality.  Other Analysis Types could be implemented here.")
