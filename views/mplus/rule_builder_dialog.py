from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from views.analysis_window_base import *
from views.data_preview_widget import *
from views.output_browser import *
from views.mplus.mplus_output_selector import *
import views.view_utilities as util

import views.workbench_launcher
import models
import datetime
import sys
import threading
import traceback
import time
from views.view_utilities import *
from views.widgets.column_chooser import *


class RuleBuilderDialog(QDialog):
    def __init__(self, input_spreadsheet, other_variables=[]):
        super(RuleBuilderDialog, self).__init__()
        self.input_spreadsheet = input_spreadsheet
        self.other_variables = other_variables
        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()

        rulePanel = self.createRulePanel()

        layout.addWidget(rulePanel)

        addButton("OK", layout, self.on_click_ok)
        addButton("Cancel", layout, self.on_click_cancel)

        self.setLayout(layout)
        column_list = self.other_variables + self.input_spreadsheet.columnnames()
        util.addColumnNamesToListView(self.columnSelectA, column_list)
        util.addColumnNamesToListView(self.columnSelectB, column_list)

    def on_click_ok(self):

        listA = util.selectedLabelsFromListView(self.columnSelectA)
        listB = util.selectedLabelsFromListView(self.columnSelectB)

        if len(listA) == 0:
            util.alert("Please select 1 or more values from the list on the right.")
            return

        if len(listB) == 0 or len(listB) > 1:
            util.alert("Please select one and only one variable on the right.")
            return

        operator = self.operatorButtonGroup.checkedButton().text()
        self.rule = (listA, operator, listB)
        self.close()

    def on_click_cancel(self):

        self.rule = None
        self.close()

    def createRulePanel(self):
        rulePanel = QWidget()
        ruleLayout = QHBoxLayout()

        self.columnSelectA = util.createColumnNameListWidget()
        self.columnSelectB = util.createColumnNameListWidget(True)

        self.ruleDisplay = QTextEdit()

        self.ruleDisplay.setVisible(False)  # we may be eliminating this UI element completely

        self.operationSelector = self.createRuleOperatorWidget()

        ruleLayout.addWidget(self.columnSelectA)
        ruleLayout.addWidget(self.operationSelector)
        ruleLayout.addWidget(self.columnSelectB)

        rulePanel.setLayout(ruleLayout)

        return rulePanel

    def createRuleOperatorWidget(self):
        group = QButtonGroup()
        groupWidget = QWidget()
        layout = QVBoxLayout()
        b1 = QRadioButton("on")
        b1.setChecked(True)
        layout.addWidget(b1)

        b2 = QRadioButton("with")
        layout.addWidget(b2)

        b3 = QRadioButton("restricted")
        layout.addWidget(b3)

        #        util.addButton("Add Rule", layout, self.add_rule)

        group.addButton(b1, 1)
        group.addButton(b2, 2)
        group.addButton(b3, 3)
        groupWidget.setLayout(layout)

        self.operatorButtonGroup = group
        return groupWidget

    def showModally(self):
        self.setWindowModality(Qt.WindowModal)
        self.show()
        self.exec_()
        return self.rule
