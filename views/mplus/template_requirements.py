from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import glob
import os
import numpy as np
from views.output_browser import *
from views import view_utilities
import sys
from views.widgets.column_chooser import *
import views.view_utilities as util

class TemplateRequirements(QWidget):
    def __init__(self):
        super(TemplateRequirements, self).__init__()

    def loadVariables(self, variables_from_template, input_spreadsheet):
        self.variables_from_template = variables_from_template
        layout = QGridLayout()
        listWidgets = {}
        col_idx = 0
        for v in variables_from_template:
            if "type" in v and "name" in v:
                if v["type"] == "column":
                    name = v["name"]

                    layout.addWidget(util.createBoldLabel(v.get("title", name) ),0, col_idx)
                    list = ColumnChooser(input_spreadsheet)
                    listWidgets[name] = list
                    layout.addWidget(list,1,col_idx)
                    col_idx += 1

        self.listWidgets = listWidgets

        self.setLayout(layout)


    def selectedValues(self):
        results = {}
        for k,v in self.listWidgets.items():
            results[k] = util.selectedLabelsFromListView(v.columnListWidget)

        return results