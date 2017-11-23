from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from views.analysis_window_base import *
from views.data_preview_widget import *
import os
import models
import subprocess
import datetime


class MplusAnalysisWindow(AnalysisWindow):
    def __init__(self, config):
        self.default_missing_tokens_list = ["-888", "NA", "", "nan"]
        self.title = "Mplus Analysis"
        self.analyzerName = "mplus"
        super(MplusAnalysisWindow, self).__init__(config)

    def open_mplus_model_template(self, path):
        self.model = models.mplus_model.MplusModel(path)
        self.modelTemplateViewer.setText(str(self.model._raw))

    def addColumnNamesToListView(self, listView, columnNames):

        model = listView.model()

        for col in columnNames:
            item = QStandardItem(col)
            # check = Qt.Checked if 1 == 1 else Qt.Unchecked
            # item.setCheckState(check)
            item.setCheckable(True)
            model.appendRow(item)

    def addInputColumnNamesToListViews(self):
        cols = ["VOXEL", "i", "q", "s", "r"] + self.input.columnnames()
        self.addColumnNamesToListView(self.columnSelectA, cols)
        self.addColumnNamesToListView(self.columnSelectB, cols)

    def createColumnNameListWidget(self, single_selection=False):
        model = QStandardItemModel()

        view = QListView()

        view.setModel(model)

        if single_selection:
            # todo #bug this is not governing the checkbox-ing, just the row level selection. we want the
            # to restrict it to single checkbox selection
            view.setSelectionMode(QAbstractItemView.SingleSelection)

        return view

    def btnstate(self, b):
        print(b.isChecked())

    def selectedLabelsFromListView(self, list):

        m = list.model()
        labels = []
        for i in range(m.rowCount()):
            item = m.item(i)
            if item.checkState() == Qt.Checked:
                labels.append(item.text())
        return labels

    def add_rule(self):

        listA = self.selectedLabelsFromListView(self.columnSelectA)
        listB = self.selectedLabelsFromListView(self.columnSelectB)

        if len(listA) == 0:
            self.alert("Please select 1 or more values from the list on the right.")
            return

        if len(listB) == 0 or len(listB) > 1:
            self.alert("Please select one and only one variable on the right.")
            return

        operator = self.operatorButtonGroup.checkedButton().text()

        # now it passes the user input to the underlying mplus model object
        self.model.add_rule(listA, operator, listB)

        self.ruleDisplay.setText(self.model.rules_to_s())

        self.updateGeneratedMPlusInputFile()

    def createRuleOperatorWidget(self):
        group = QButtonGroup()
        groupWidget = QWidget()
        layout = QVBoxLayout()
        b1 = QRadioButton("on")
        b1.setChecked(True)
        b1.toggled.connect(lambda: self.btnstate(b1))
        layout.addWidget(b1)

        b2 = QRadioButton("with")
        b2.toggled.connect(lambda: self.btnstate(b2))
        layout.addWidget(b2)

        b3 = QRadioButton("restricted")
        b3.toggled.connect(lambda: self.btnstate(b3))
        layout.addWidget(b3)

        addBtn = QPushButton("Add Rule")
        addBtn.clicked.connect(self.add_rule)

        layout.addWidget(addBtn)
        group.addButton(b1, 1)
        group.addButton(b2, 2)
        group.addButton(b3, 3)
        groupWidget.setLayout(layout)

        self.operatorButtonGroup = group
        return groupWidget

    def initModelBuilderPanel(self):

        rulePanel = QWidget()
        ruleLayout = QHBoxLayout()

        self.columnSelectA = self.createColumnNameListWidget()
        self.columnSelectB = self.createColumnNameListWidget(True)

        self.ruleDisplay = QTextEdit()

        self.operationSelector = self.createRuleOperatorWidget()

        ruleLayout.addWidget(self.columnSelectA)
        ruleLayout.addWidget(self.operationSelector)
        ruleLayout.addWidget(self.columnSelectB)

        rulePanel.setLayout(ruleLayout)

        self.modelBuilderLayout.addWidget(rulePanel)

        self.modelBuilderLayout.addWidget(self.ruleDisplay)

    def initModelBuilder(self):
        self.modelBuilder = QWidget()
        self.modelBuilderLayout = QVBoxLayout()
        self.modelBuilderLayout.addWidget(QLabel("Select Covariates"))
        self.modelBuilder.setLayout(self.modelBuilderLayout)
        self.initModelBuilderPanel()

    def addTopLevelOptionWidgets(self):

        self.verticalGroupBox.layout()
        self.verticalGroupBox.layout().addWidget(QLabel("Title:"))
        self.titleEdit = QLineEdit()
        self.titleEdit.setText("DefaultTitle")
        self.verticalGroupBox.layout().addWidget(self.titleEdit)

    def initUISpecific(self):

        self.addTopLevelOptionWidgets()

        self.initModelBuilder()

        self.modelTemplateViewer = QTextEdit()
        self.generatedModelViewer = QTextEdit()

        self.dataPreview = DataPreviewWidget()

        self.modelOutput = QTextEdit()

        newMplusModel = QWidget()

        self.modelDesignContainer = QVBoxLayout()
        self.modelDesignContainer.addWidget(self.generatedModelViewer)
        newMplusModel.setLayout(self.modelDesignContainer)

        self.addTab(self.dataPreview, "Input Data Review")
        self.addTab(self.modelTemplateViewer, "Model Template")
        self.addTab(self.modelBuilder, "Model Builder")
        self.addTab(newMplusModel, "New Mplus Model")
        self.addTab(self.modelOutput, "Raw MPlus Output")

        self.tabs.setCurrentIndex(0)

    def updateUIAfterInput(self):

        self.addInputColumnNamesToListViews()

    def updateGeneratedMPlusInputFile(self, save_to_path=""):
        columns = self.input.columnnames()

        self.model.set_column_names(columns)

        generated_mplus_model = self.model.to_string()
        self.generatedModelViewer.setText(generated_mplus_model)

        if False:

            if len(save_to_path) > 0:
                with open(save_to_path, "w") as f:
                    f.write(self.model.to_string())

    def launchWorkbench(self, cifti_output_path):
        base_image_paths = "/Users/David/Documents/projects/mastergui/data/fsaverage_LR32k/ohsu-sub-NDARINV3F6NJ6WW.L.inflated.32k_fs_LR.surf.gii /Users/David/Documents/projects/mastergui/data/fsaverage_LR32k/ohsu-sub-NDARINV3F6NJ6WW.L.midthickness.32k_fs_LR.surf.gii /Users/David/Documents/projects/mastergui/data/fsaverage_LR32k/ohsu-sub-NDARINV3F6NJ6WW.L.pial.32k_fs_LR.surf.gii /Users/David/Documents/projects/mastergui/data/fsaverage_LR32k/ohsu-sub-NDARINV3F6NJ6WW.R.inflated.32k_fs_LR.surf.gii /Users/David/Documents/projects/mastergui/data/fsaverage_LR32k/ohsu-sub-NDARINV3F6NJ6WW.R.midthickness.32k_fs_LR.surf.gii /Users/David/Documents/projects/mastergui/data/fsaverage_LR32k/ohsu-sub-NDARINV3F6NJ6WW.R.pial.32k_fs_LR.surf.gii /Users/David/Documents/projects/mastergui/data/T1w_restore.nii.gz"

        # todo require wb_view is in the users path and change this mac specific command
        os.system(
            'open -a "/Applications/connectomeworkbench/macosx64_apps/wb_view.app" --args ' + base_image_paths + " " + cifti_output_path)

    def Go(self):
        self.modelOutput.setText("Pending...")

        title = self.titleEdit.text() + str(datetime.datetime.now()).replace(" ", ".").replace(":", ".")

        self.model.title = title

        analysis = models.mplus_analysis.MplusAnalysis(self.config)

        # for testing, halt after n rows of data processing. Set to 0 to do everything.
        halt_after_n = 3
        mplus_output_contents = analysis.go(self.model, self.titleEdit.text(), self.input,
                                            self.dataPreview.missing_tokens, halt_after_n)

        self.modelOutput.setText(mplus_output_contents)

        self.tabs.setCurrentIndex(5)

        cifti_output_path = analysis.cifti_output_path

        if len(cifti_output_path)>0:
            self.launchWorkbench(cifti_output_path)
