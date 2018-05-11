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
from models.post_processing import *

class MPlusPostProcessingOptionsEditor(QDialog):
    def __init__(self,config, pp_command_name, path_to_cifti):

        super(MPlusPostProcessingOptionsEditor, self).__init__()

        self.pp = PostProcessing(config)

        self.initial_lines = self.pp.build_parameter_file(pp_command_name, path_to_cifti)

        self.cancelled = False

        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()

        self.text = QTextEdit()
        self.text.setText(self.initial_lines)

        layout.addWidget(self.text)

        addButton("OK", layout, self.on_click_ok)
        addButton("Cancel", layout, self.on_click_ok)
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.setLayout(layout)

    def validate(self):
        #if your subclass needs validation logic when the user hits ok
        #override this method in the subclass
        return True

    def on_click_ok(self):
        if self.validate():
            self.close()

    def on_click_cancel(self):
        self.cancelled = True
        self.close()

    def showModally(self):
        self.setWindowModality(Qt.WindowModal)
        self.show()
        self.exec_()

    def selectedRow(self):
        return self.chooser.selectedRow()
