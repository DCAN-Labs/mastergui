from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from views.analysis_window_base import *
from views.data_preview_widget import *
import views.workbench_launcher
import models
import datetime
import sys


class MplusAnalysisWindow(AnalysisWindow):
    def __init__(self, config):
        self.default_missing_tokens_list = ["-888", "NA", "", "nan"]
        self.title = "Mplus Analysis"
        self.analyzerName = "mplus"
        super(MplusAnalysisWindow, self).__init__(config)

        a = models.mplus_analysis.MplusAnalysis(self.config)

        missing_keys = a.missingRequiredConfigKeys()

        if len(missing_keys) > 0:
            self.alert("Your configuration file is missing some items that are required for the full functionality.  Please provide the following keys: " + " ".join(missing_keys))

        data_path = self.config.getOptional("open_path_on_launch","")
        if len(data_path)==0:
            self.openDataFileDialog()
        else:
            self.open_input_file(data_path)

        filename = self.config.getOptional("open_mplus_model_on_launch", "")
        self.needsTemplate = True
        if len(filename) > 0:
            if os.path.exists(filename):
                self.open_mplus_model_template_from_file(filename)
                self.needsTemplate = False
            else:
                self.alert(
                    filename + " does not exist. Check your config.yml file attribute open_mplus_model_on_launch.")

        if not self.needsTemplate:
            self.tabs.setTabEnabled(0, False)
            #source of this stylesheet trick to hide disabled tab:
            # https://stackoverflow.com/questions/34377663/how-to-hide-a-tab-in-qtabwidget-and-show-it-when-a-button-is-pressed
            self.tabs.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")



    def openDataFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select Data File", "","All Data Files (*.csv *.xls *.xlsx);;Excel Files (*.xls *.xlsx);;CSV files (*.csv)", options=options)
        if fileName:
            self.fileName = fileName
            self.open_input_file(fileName)

    def open_mplus_model_template_from_file(self, path):
        self.model = models.mplus_model.MplusModel(path)
        self.modelTemplateViewer.setText(str(self.model._raw))

    def open_mplus_model_raw(self, model_text):
        self.model = models.mplus_model.MplusModel()
        self.model.loadFromString(model_text)
        self.modelTemplateViewer.setText(model_text)

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

        self.progress = QProgressBar()

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
        try:
            views.workbench_launcher.launch(self.config, cifti_output_path)
        except:
            info = sys.exc_info()
            self.alert("Error opening workbench.\n%s\n%s" % (info[0],info[1]))
            print(info)

    def activateProgressBar(self):
        self.progress.show()
        self.progress.setMaximum(len(self.input.data()))
        self.progress.setValue(len(self.input.data()) / 2)

    def Go(self):

        #self.activateProgressBar()

        self.modelOutput.setText("Pending...")

        title = self.titleEdit.text() + str(datetime.datetime.now()).replace(" ", ".").replace(":", ".")

        self.model.title = title

        analysis = models.mplus_analysis.MplusAnalysis(self.config)

        # for testing, halt after n rows of data processing. Set to 0 to do everything.
        halt_after_n = int(self.config.getOptional('testing_halt_after_n_voxels',3))

        mplus_output_contents = analysis.go(self.model, self.titleEdit.text(), self.input,
                                            self.dataPreview.missing_tokens, halt_after_n)

        self.modelOutput.setText(mplus_output_contents)

        self.tabs.setCurrentIndex(5)

        cifti_output_path = analysis.cifti_output_path

        if len(cifti_output_path)>0:
            self.launchWorkbench(cifti_output_path)

