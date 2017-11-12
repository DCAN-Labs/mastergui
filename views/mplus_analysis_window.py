from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from views.analysis_window_base import *
import os
import models
import subprocess


class MplusAnalysisWindow(AnalysisWindow):
    def __init__(self, config):
        self.default_missing_tokens_list = ["-888", "NA", "", "nan"]
        self.title = "Mplus Analysis"
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
        cols = self.input.columnnames() + ["i", "q", "s", "r"]
        self.addColumnNamesToListView(self.columnSelectA, cols)
        self.addColumnNamesToListView(self.columnSelectB, cols)

    def createColumnNameListWidget(self, single_selection=False):
        model = QStandardItemModel()

        view = QListView()

        view.setModel(model)

        if single_selection:
            #todo #bug this is not governing the checkbox-ing, just the row level selection. we want the
            #to restrict it to single checkbox selection
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

        #now it passes the user input to the underlying mplus model object
        self.model.add_rule(listA, operator, listB)

        self.ruleDisplay.setText(self.model.rules_to_s())

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

    def initUISpecific(self):
        self.analysisOptionsLayout.addWidget(QLabel("Missing Data Tokens:"))
        self.missingDataTokens = QLineEdit()
        self.missingDataTokens.setText(",".join(self.default_missing_tokens_list))
        self.analysisOptionsLayout.addWidget(self.missingDataTokens)

        self.modelTemplateViewer = QTextEdit()
        self.generatedModelViewer = QTextEdit()
        self.modelBuilder = QWidget()
        self.modelBuilderLayout = QVBoxLayout()
        self.modelBuilderLayout.addWidget(QLabel("Select Covariates"))
        self.modelBuilder.setLayout(self.modelBuilderLayout)
        self.inputTable = QTableWidget()
        self.modelOutput = QTextEdit()

        self.tabs = QTabWidget()

        x = QWidget()

        self.modelDesignContainer = QVBoxLayout()
        self.modelDesignContainer.addWidget(self.generatedModelViewer)
        x.setLayout(self.modelDesignContainer)
        self.tabs.resize(300, 200)
        self.tabs.addTab(self.inputTable, "Input Data Review")
        self.tabs.addTab(self.modelTemplateViewer, "Model Template")
        self.tabs.addTab(self.modelBuilder, "Model Builder")
        self.tabs.addTab(x, "New Mplus Model")
        self.tabs.addTab(self.modelOutput, "Raw MPlus Output")
        self.grid.addWidget(self.tabs)

        self.initModelBuilderPanel()

    def updateUIAfterInput(self):

        self.addInputColumnNamesToListViews()

    def Go(self):
        # make data file with characters replaced
        output_path = os.path.join(self.config._data.get("output_dir", ""), "GENERATEDmissing.csv")
        self.input.save_cleaned_data(output_path, self.default_missing_tokens_list)
        # make mplus analysi file
        self.alert(output_path + " successfully saved.")

        columns = self.input.columnnames()

        self.model.set_column_names(columns)

        generated_mplus_model = self.model.to_string()
        self.generatedModelViewer.setText(generated_mplus_model)
        # launch mplus

        os.system('sox input.wav -b 24 output.aiff rate -v -L -b 90 48k')

        # todo safety check this in case of rogue yml input!

        model_input_file_path = os.path.join(self.config._data["output_dir"], "tempmodel.inp")

        model_output_file_path = model_input_file_path + ".out"

        with open(model_input_file_path, "w") as f:
            f.write(generated_mplus_model)

        cmd = self.config._data["MPlus_command"] + " " + model_input_file_path

        print("About to run command\n", cmd)

        os.system(cmd)

        result = subprocess.run([self.config._data["MPlus_command"],
                                 model_input_file_path,
                                 model_output_file_path], stdout=subprocess.PIPE)

        with open(model_output_file_path, "r") as f:
            mplus_output_contents = f.read()

        self.modelOutput.setText(mplus_output_contents)

        print(str(result.stdout, 'utf-8'))
