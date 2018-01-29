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
from views.widgets.column_chooser_dropdown import *
import views.view_utilities as util


class TemplateRequirements(QGroupBox):
    def __init__(self):
        super(TemplateRequirements, self).__init__("Template Requirements")
        self.setFont(util.boldQFont())
        self.setFlat(True)

    # def loadVariablesAsLists(self, variables_from_template, input_spreadsheet, non_spreadsheet_variables = []):
    #     self.variables_from_template = variables_from_template
    #     self.non_spreadsheet_variables = non_spreadsheet_variables
    #     layout = QGridLayout()
    #     listWidgets = {}
    #     col_idx = 0
    #     for v in variables_from_template:
    #         if "type" in v and "name" in v:
    #             if v["type"] == "column":
    #                 name = v["name"]
    #
    #                 if "default" in v:
    #                     default = v["default"]
    #                 else:
    #                     default = None
    #                 layout.addWidget(util.createBoldLabel(v.get("title", name) ),0, col_idx)
    #                 list = ColumnChooser(input_spreadsheet, default)
    #                 listWidgets[name] = list
    #                 layout.addWidget(list,1,col_idx)
    #                 col_idx += 1
    #
    #     self.listWidgets = listWidgets
    #
    #     self.setLayout(layout)

    def loadVariables(self, variables_from_template, input_spreadsheet, non_spreadsheet_variables=[]):
        self.variables_from_template = variables_from_template
        self.non_spreadsheet_variables = non_spreadsheet_variables
        self.input_spreadsheet = input_spreadsheet
        layout = QFormLayout()
        listWidgets = {}
        for v in variables_from_template:
            if "default" in v:
                default = v["default"]
            else:
                default = ""

            if "type" in v and "name" in v:
                if v["type"] == "column":
                    name = v["name"]

                    label = util.createBoldLabel(v.get("title", name))
                    list = ColumnChooserDropDown(input_spreadsheet, self.non_spreadsheet_variables, default)
                    listWidgets[name] = list
                    layout.addRow(label, list)

        self.listWidgets = listWidgets

        self.setLayout(layout)

    def selectedValues(self):
        results = {}
        for k, v in self.listWidgets.items():
            type_of_widget = type(v)
            if type_of_widget == ColumnChooserDropDown:
                results[k] = v.currentText()
            elif type_of_widget == ColumnChooser:
                results[k] = util.selectedLabelsFromListView(v.columnListWidget)

        return results

    def updateInputSpreadsheet(self, input):
        self.input_spreadsheet = input
        self.refreshColumns()

    def updateNonSpreadsheetVariables(self, non_spreadsheet_variables):
        self.non_spreadsheet_variables = non_spreadsheet_variables

        self.refreshColumns()

    def refreshColumns(self):
        for k, v in self.listWidgets.items():
            v.updateInputSpreadsheet(self.input_spreadsheet, self.non_spreadsheet_variables)
