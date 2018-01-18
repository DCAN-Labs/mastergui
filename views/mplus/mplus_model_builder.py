from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from views.analysis_window_base import *
from views.data_preview_widget import *
from views.output_browser import *
from views.mplus.mplus_output_selector import *
from views.mplus.template_requirements import *
import views.view_utilities as util
import views.workbench_launcher
import models
import datetime
import sys
import threading
import traceback
import time


class MplusModelBuilder(QWidget):
    def __init__(self, parentAnalysis):
        super(MplusModelBuilder, self).__init__()
        self.variables_loaded = False
        self.parentAnalysis = parentAnalysis
        self.initModelBuilder()

    def initModelBuilder(self):
        """
        structure of widgets:
            modelBuilderTab (Hbox)
                modelBuilder   (choosers for specifying rules that go into the model

                modelBuilderTemplateViewTabs
                    model view widget
                    template view widget
        :return:
        """

        top_level_layout = QHBoxLayout()

        self.modelBuilderTemplateViewTabs = QTabWidget()

        self.left_panel = self.createLeftPanel()


        self.initModelBuilderViewTabs()

        top_level_layout.addWidget(self.left_panel,stretch=6)
        top_level_layout.addWidget(self.modelBuilderTemplateViewTabs,stretch=4)

        self.loadVariables()

        self.setLayout(top_level_layout)


    def createLeftPanel(self):

        panelWidget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Covariates"))


        rulePanel = QWidget()
        ruleLayout = QHBoxLayout()

        self.columnSelectA = util.createColumnNameListWidget()
        self.columnSelectB = util.createColumnNameListWidget(True)

        self.ruleDisplay = QTextEdit()

        self.ruleDisplay.setVisible(False) #we may be eliminating this UI element completely
        self.operationSelector = self.createRuleOperatorWidget()

        ruleLayout.addWidget(self.columnSelectA)
        ruleLayout.addWidget(self.operationSelector)
        ruleLayout.addWidget(self.columnSelectB)

        rulePanel.setLayout(ruleLayout)

        layout.addWidget(rulePanel)

        layout.addWidget(self.ruleDisplay)

        panelWidget.setLayout(layout)

        return panelWidget

    def initModelBuilderViewTabs(self):
        self.modelTemplateViewer = QTextEdit()
        self.generatedModelViewer = QTextEdit()

        self.modelBuilderTemplateViewTabs.addTab(self.generatedModelViewer, "Model")
        self.modelBuilderTemplateViewTabs.addTab(self.modelTemplateViewer, "Template")

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

        util.addButton("Add Rule", layout, self.add_rule)

        group.addButton(b1, 1)
        group.addButton(b2, 2)
        group.addButton(b3, 3)
        groupWidget.setLayout(layout)

        self.operatorButtonGroup = group
        return groupWidget

    def add_rule(self):

        listA = util.selectedLabelsFromListView(self.columnSelectA)
        listB = util.selectedLabelsFromListView(self.columnSelectB)

        if len(listA) == 0:
            self.alert("Please select 1 or more values from the list on the right.")
            return

        if len(listB) == 0 or len(listB) > 1:
            self.alert("Please select one and only one variable on the right.")
            return

        operator = self.operatorButtonGroup.checkedButton().text()

        # now it passes the user input to the underlying mplus model object
        self.parentAnalysis.model.add_rule(listA, operator, listB)

        self.ruleDisplay.setText(self.parentAnalysis.model.rules_to_s())

        self.updateGeneratedMPlusInputFile()

        self.parentAnalysis.dataPreview.update_selected_checks_from_analysis(self.parentAnalysis.model)


    def updateGeneratedMPlusInputFile(self, save_to_path=""):
        columns = self.parentAnalysis.input.columnnames()

        self.parentAnalysis.model.set_voxelized_mappings(self.parentAnalysis.dataPreview.selected_voxelized_columns())

        self.parentAnalysis.model.set_column_names(columns)

        generated_mplus_model = self.parentAnalysis.model.to_string()

        self.generatedModelViewer.setText(generated_mplus_model)

    def refresh(self):
        self.addInputColumnNamesToListViews()

    def loadVariables(self):

        if self.variables_loaded:
            return
        if hasattr(self.parentAnalysis, "template") and hasattr(self.parentAnalysis, "input"):
            v = self.parentAnalysis.template.variables
            if len(v) > 0:
                template_requirements = TemplateRequirements()
                template_requirements.loadVariables(v, self.parentAnalysis.input)
                template_requirements.setMaximumWidth(600)
                self.left_panel.layout().insertWidget(0,template_requirements)
                self.template_requirements = template_requirements
                self.variables_loaded = True

                button = QPushButton("Apply")
                button.clicked.connect(self.on_click_apply_template_variables)
                self.left_panel.layout().insertWidget(1,button)


    def on_click_apply_template_variables(self):
        options = self.template_requirements.selectedValues()

        # todo temporary hack until change the list do drop down list, just want one item per
        # at the moment
        for k, v in options.items():
            colname = v[0]
            options[k] = colname




        generated_mplus_model = self.parentAnalysis.model.apply_options(options)

        self.generatedModelViewer.setText(generated_mplus_model)


    def addInputColumnNamesToListViews(self):

        cols = ["i", "q", "s", "r"] + self.parentAnalysis.dataPreview.possibleColumnNames()
        util.addColumnNamesToListView(self.columnSelectA, cols)
        util.addColumnNamesToListView(self.columnSelectB, cols)

        #        if hasattr(self,"template_requirements"):
        #            self.template_requirements.loadVariables(self.template.variables, self.input)


        self.loadVariables()

