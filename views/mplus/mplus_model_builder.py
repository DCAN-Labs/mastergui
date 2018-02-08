from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from views.analysis_window_base import *
from views.widgets.data_preview_widget import *
from views.output_browser import *
from views.mplus.mplus_output_selector import *
from views.mplus.template_requirements import *
import views.view_utilities as util
from views.widgets.column_list import *
from views.mplus.voxelizer_dialog import *
from views.mplus.rule_builder_dialog import *
import views.workbench_launcher
import models
import datetime
import sys
import threading
import traceback
import time


class MplusModelBuilder(QWidget):
    def __init__(self):
        super(MplusModelBuilder, self).__init__()
        self.variables_loaded = False
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

        top_level_layout.addWidget(self.left_panel, stretch=6)
        top_level_layout.addWidget(self.modelBuilderTemplateViewTabs, stretch=4)

        self.loadVariables()

        util.addButton("Apply", self.left_panel.layout(), self.on_click_apply_template_variables, 140 )

        self.setLayout(top_level_layout)

    def createLeftPanel(self):

        panelWidget = QWidget()
        layout = QVBoxLayout()
        # layout.addWidget(QLabel("Select Covariates"))

        w = self.createColumnsWidgets()
        layout.addWidget(w)

        # rulePanel = self.createRulePanel()

        # layout.addWidget(rulePanel)
        # rulePanel.setVisible(False)
        # layout.addWidget(self.ruleDisplay)
        self.rule_list_widget = self.createRuleListWidget()
        layout.addWidget(self.rule_list_widget)

        panelWidget.setLayout(layout)

        return panelWidget

    def createColumnsWidgets(self):
        w = QGroupBox("Created Variables")
        #w.setAutoFillBackground(True)
        w.setFlat(True)
        w.setFont(util.boldQFont())

        layout = QHBoxLayout()
        layout.setContentsMargins(2,2,2,2)
        self.voxelized_list = ColumnList("Voxelized Columns")
        self.voxelized_list.setFixedHeight(150)
        self.voxelized_list.setAddClickHandler(self.on_click_add_voxelized_column)
        self.voxelized_list.setRemoveClickHandler(self.on_click_remove_voxelized_column)
        layout.addWidget(self.voxelized_list)

        self.other_variables_list = ColumnList("Latent Variables")
        self.other_variables_list.setFixedHeight(150)

        layout.addWidget(self.other_variables_list)

        w.setLayout(layout)
        return w

    def on_click_add_voxelized_column(self):
        d = VoxelizerDialog(self.analysis.input)
        mapping = d.mapping()

        if not mapping is None:
            self.addVoxelizedColumn(mapping[0], mapping[1])

    def displayVoxelizedColumns(self):
        display_list = []
        for mapping in self.analysis.voxelized_column_mappings:
            display_list.append("%s => %s" % mapping)

        self.voxelized_list.loadValues(display_list)

    def on_click_remove_voxelized_column(self):

        value = self.voxelized_list.selectedRow()
        if not value is None:
            parsed = value.split(" => ")
            self.analysis.removeVoxelizedColumn(parsed[0], parsed[1])
            self.refreshNonDataColumnViews()
            self.displayVoxelizedColumns()

    def createRuleListWidget(self):
        w = QGroupBox("Additional Model Rules")
        w.setFlat(True)
        w.setFont(util.boldQFont())
        layout = QHBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        rule_list = ColumnList("")
        rule_list.setAddClickHandler(self.add_rule)
        rule_list.setFixedHeight(150)
        rule_list.setRemoveClickHandler(self.remove_rule)
        self.rule_list = rule_list
        layout.addWidget(rule_list)
        w.setLayout(layout)
        return w

    def initModelBuilderViewTabs(self):
        self.modelTemplateViewer = QTextEdit()
        self.generatedModelViewer = QTextEdit()

        self.modelBuilderTemplateViewTabs.addTab(self.generatedModelViewer, "Model")
        self.modelBuilderTemplateViewTabs.addTab(self.modelTemplateViewer, "Template")

    def add_rule(self):

        rbd = RuleBuilderDialog(self.analysis.input, self.all_nonspreadsheet_variables_to_display())
        rule = rbd.showModally()

        if rule is not None:
            # now it passes the user input to the underlying mplus model object
            self.analysis.model.add_rule(*rule)
            self.rule_list.loadValues(self.analysis.model.rules)
            # self.ruleDisplay.setText(self.analysis.model.rules)

            self.updateGeneratedMPlusInputFile()

            self.parentAnalysisWindow.dataPreview.update_selected_checks_from_analysis(self.analysis.model)

    def remove_rule(self):
        # todo implement remove rule
        print("remove rule")
        rule = self.rule_list.selectedRow()
        if rule is not None:
            self.analysis.model.remove_rule_by_string(rule)
            self.rule_list.loadValues(self.analysis.model.rules)
            # self.ruleDisplay.setText(self.analysis.model.rules)

            self.updateGeneratedMPlusInputFile()

            self.parentAnalysisWindow.dataPreview.update_selected_checks_from_analysis(self.analysis.model)

    def updateGeneratedMPlusInputFile(self, save_to_path=""):
        columns = self.analysis.input.columnnames()

        # self.analysis.model.set_voxelized_mappings(self.analysis.voxelized_column_mappings)

        self.analysis.model.set_column_names(columns)

        generated_mplus_model = self.analysis.model.to_string()

        self.generatedModelViewer.setText(generated_mplus_model)

    def refresh(self):
        self.addInputColumnNamesToListViews()

    def loadVariables(self):
        if not hasattr(self, "analysis"):
            return
        if self.variables_loaded:
            return
        if hasattr(self.analysis, "template"):
            v = self.analysis.template.variables
            if len(v) > 0:
                template_requirements = TemplateRequirements()

                if hasattr(self.analysis, "input"):
                    input = self.analysis.input
                else:
                    input = None
                template_requirements.loadVariables(v, input)
                template_requirements.setMaximumWidth(600)
                self.left_panel.layout().insertWidget(1, template_requirements, stretch=5)
                self.template_requirements = template_requirements
                self.variables_loaded = True


    def on_click_apply_template_variables(self):
        options = self.template_requirements.selectedValues()

        generated_mplus_model_text = self.analysis.updateModel(options, self.all_nonspreadsheet_variables_to_display())

        self.generatedModelViewer.setText(generated_mplus_model_text)

    def addInputColumnNamesToListViews(self):

        # cols = ["i", "q", "s", "r"] + self.parentAnalysis.dataPreview.possibleColumnNames()
        # todo restore column refreshing if necessary in the updated ui

        # util.addColumnNamesToListView(self.columnSelectA, cols)
        # util.addColumnNamesToListView(self.columnSelectB, cols)
        print("what else to refresh?")

    def updateDataColumns(self):
        if hasattr(self, "template_requirements"):
            self.template_requirements.updateInputSpreadsheet(self.analysis.input)

    def loadAnalysis(self, analysis, parentAnalysisWindow):

        self.analysis = analysis
        self.loadVariables()
        self.parentAnalysisWindow = parentAnalysisWindow
        self.rule_list.loadValues(self.analysis.model.rules)
        self.displayVoxelizedColumns()

    def all_nonspreadsheet_variables_to_display(self):

        if hasattr(self, "analysis"):
            cols = [m[1] for m in self.analysis.voxelized_column_mappings]
            # todo if and only if analysis should show time series related columns (add attribute to template json)
            cols += ["i", "q", "s", "r"]
        else:
            cols = ["i", "q", "s", "r"]
        return cols

    def addVoxelizedColumn(self, from_col, new_colname):
        self.analysis.addVoxelizedColumn(from_col, new_colname)

        self.refreshNonDataColumnViews()

        self.displayVoxelizedColumns()

    def refreshNonDataColumnViews(self):
        if hasattr(self, "template_requirements"):
            self.template_requirements.updateNonSpreadsheetVariables(self.all_nonspreadsheet_variables_to_display())

    def autoVoxelize(self):
        """by convention we will assume that any column names that start with "PATH_" are intended for voxelization
        """

        if hasattr(self, "analysis"):
            columns = self.analysis.input.columnnames()

            for colname in columns:
                if colname[0:5] == "PATH_":
                    new_colname = "VOXEL_" + colname[5:]

                    self.addVoxelizedColumn(colname, new_colname)
