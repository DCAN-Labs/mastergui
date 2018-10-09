from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import views.workbench_launcher
import models
import datetime
import sys
import threading
import traceback
import time
from views.mplus import *
from views.analysis_window_base import *
from views.widgets.data_preview_widget import *
from views.output_browser import *
from views.mplus.mplus_output_selector import *
from views.mplus.template_requirements import *
from views.mplus.mplus_model_builder import *
from views.mplus.mplus_postprocessing_options import *
from views.workers import *
from views.widgets import *
from views.mplus import *
# from views.mplus.mplus_output_selector import *

import views.mplus.output_chooser_dialog

tab_datapreview = 1
tab_modelbuilder = 2
tab_execute = 3
tab_test = 3
tab_run = 4
tab_output = 5
tab_outputselector = 6


class MplusAnalysisWindow(AnalysisWindow):
    def __init__(self, config, analysis=None):
        self.title = "Mplus Analysis"
        self.analyzerName = "mplus"
        super(MplusAnalysisWindow, self).__init__(config)

        analysis_was_provided = analysis is not None

        if analysis is None:
            analysis = models.mplus_analysis.MplusAnalysis(self.config)

        self.analysis = analysis

        self.validateConfiguration()

        self.needsTemplate = not analysis_was_provided

        self.loadAnalysis(analysis)

        if not self.needsTemplate:
            self.tabs.setTabEnabled(0, False)
            # source of this stylesheet trick to hide disabled tab:
            # https://stackoverflow.com/questions/34377663/how-to-hide-a-tab-in-qtabwidget-and-show-it-when-a-button-is-pressed
        self.tabs.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")

    def handle_open_specifically(self, file_contents):
        """for subclass overriding"""
        print("implement in subclass")

    def openDataFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Data File", "",
                                                  "All Data Files (*.csv *.xls *.xlsx);;Excel Files (*.xls *.xlsx);;CSV files (*.csv)",
                                                  options=options)
        if fileName:
            self.fileName = fileName
            self.open_input_file(fileName)

    def open_input_file(self, path):
        super(MplusAnalysisWindow, self).open_input_file(path)
        self.modelBuilder.updateDataColumns()
        self.modelBuilder.autoVoxelize()

    def open_mplus_model_template_from_file(self, path):
        self.model = models.mplus_model.MplusModel(path)
        self.modelTemplateViewer.setText(str(self.model._raw))
        self.analysis.model = self.model

    def open_mplus_model_raw(self, model_text):
        self.model = models.mplus_model.MplusModel()
        self.model.loadFromString(model_text)
        self.modelBuilder.modelTemplateViewer.setText(model_text)
        self.analysis.model = self.model

    def selectedLabelsFromListView(self, list):

        m = list.model()
        labels = []
        for i in range(m.rowCount()):
            item = m.item(i)
            if item.checkState() == Qt.Checked:
                labels.append(item.text())
        return labels

    def initUISpecific(self):
        """
        This method is invoked by the base class upon initial loading and should contain the GUI
        initialization code specific to this particular analysis module
        :return:
        """
        self.initModelSelection()

        self.initModelBuilder()

        self.dataPreview = DataPreviewWidget(self)

        self.initExecuteTab()

        self.addTab(self.dataPreview, "Input Data Review")
        self.addTab(self.modelBuilder, "Model Builder")
        self.addTab(self.execAnalysisWidget, "Execute")
        self.initOutputTab()

        self.tabs.setCurrentIndex(0)

        self.progress = QProgressBar()

        [self.tabs.setTabEnabled(i, False) for i in range(1, self.tabs.count())]

    def initOutputTab(self):

        self.outputViewer = MplusOutputSelector(self)

        self.addTab(self.outputViewer, "Output")

    def onTabChanged(self, p_int):
        # print("tab select %d " % p_int)
        if p_int == tab_modelbuilder:
            self.modelBuilder.refresh()
        # elif p_int == tab_modelbuilder:
        #    self.dataPreview.update_selected_checks_from_analysis(self.model)
        elif p_int == tab_execute:
            self.outputViewer.on_click_refresh()
            # elif p_int == tab_outputselector:
            #    self.outputSelector.on_click_refresh()

    def initOutputTabs(self):

        self.outputTabs = QTabWidget()

        self.outputTabs.addTab(self.modelOutput, "Status")
        # self.outputViewer = MplusOutputSelector(self)
        # self.outputTabs.addTab(self.outputViewer, "Output")

        # self.outputSelector = MplusOutputSelector(self)
        # self.outputTabs.addTab(self.outputSelector, "Output Value Selector")

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

        # self.modelBuilderTab = QWidget()
        # self.modelBuilderTabLayout = QHBoxLayout()
        # self.modelBuilderTab.setLayout(self.modelBuilderTabLayout)

        # self.modelBuilderTemplateViewTabs = QTabWidget()

        self.modelBuilder = MplusModelBuilder()


        # self.modelBuilderTabLayout.addWidget(self.modelBuilder)
        # self.modelBuilderTabLayout.addWidget(self.modelBuilderTemplateViewTabs)

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

    def initModelBuilderViewTabs(self):
        self.modelTemplateViewer = QTextEdit()
        self.generatedModelViewer = QTextEdit()

        self.modelBuilderTemplateViewTabs.addTab(self.generatedModelViewer, "Model")
        self.modelBuilderTemplateViewTabs.addTab(self.modelTemplateViewer, "Template")

    def initExecuteTab(self):
        self.execAnalysisWidget = QWidget()
        self.modelOutput = QTextEdit()

        l = QVBoxLayout()

        command_bar = QHBoxLayout()

        self.initTestAnalysisFrame(command_bar)

        command_box = QVBoxLayout()

        self.chkAutoLaunchWorkbench = QCheckBox("Launch Workbench When Complete")
        self.chkAutoLaunchWorkbench.setChecked(True)

        command_box.addWidget(self.chkAutoLaunchWorkbench)

        self.runBtn = self.addButton("Run Analysis", command_box, self.runAnalysis, 130)

        self.cancelBtn = self.addButton("Cancel Analysis", command_box, self.on_click_cancel, width=130)
        self.cancelBtn.setEnabled(False)

        self.outputParameterChoiceList = ColumnList("Output Parameters",
                                                    self.on_click_add_output_parameter,
                                                    self.on_click_remove_output_parameter,
                                                    checkable=False)
        self.outputParameterChoiceList.setFixedHeight(150)

        command_bar.addWidget(self.outputParameterChoiceList)

        command_bar.addLayout(command_box)

        l.addLayout(command_bar)

        self.initOutputTabs()

        l.addWidget(self.outputTabs)

        self.execAnalysisWidget.setLayout(l)

    def on_click_add_output_parameter(self):

        path = self.analysis.modelOutputPathByVoxel(0) + ".out"
        if os.path.exists(path):
            c = OutputChooserDialog(path)
            # @ Darrick if c.selection is list...
            if isinstance(c.selection, list):
                for selection in c.selection:
                    self.addOutputParameter(selection)
            elif c.selection:
                self.addOutputParameter(c.selection)
        else:
            util.alert(
                "Sample output not found. Run Test Analysis first so that you have some sample Mplus output from which you can choose columns.")

    def on_click_remove_output_parameter(self):
        value = self.outputParameterChoiceList.selectedRow()
        if value:
            if value in self.analysis.output_parameters:
                self.analysis.output_parameters.remove(value)
        self.loadOutputParameterChoices()

    def loadOutputParameterChoices(self):

        self.outputParameterChoiceList.loadValues(self.analysis.output_parameters)

    def on_click_cancel(self):
        close_msg = "Are you sure you want to cancel the execution of this analysis in progress?"
        reply = QMessageBox.question(self, 'Message',
                                     close_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.appendTextToOutputDisplay("Attempting to cancel...")
            self.cancelling = True
            self.analysis.cancelAnalysis()
            self.cancelBtn.setEnabled(False)

    def addCheckBoxAndField(self, container, checkLabel, fieldInitialValue):
        row = QHBoxLayout()
        fld = QLineEdit(str(fieldInitialValue))
        fld.setFixedWidth(30)
        chk = QCheckBox(checkLabel)
        chk.setChecked(True)
        row.addWidget(chk)
        row.addWidget(fld)

        container.addLayout(row)

        return (chk, fld)

    def initTestAnalysisFrame(self, container):

        optionsFrame = QFrame()
        optionsFrame.setFixedWidth(250)
        optionsFrame.setFrameShape(QFrame.StyledPanel)

        options = QVBoxLayout()

        self.checkLimitRows, self.wLimitRows = self.addCheckBoxAndField(options, "Limit # of rows", 10)
        self.checkLimitVoxels, self.wLimitVoxels = self.addCheckBoxAndField(options, "Limit # of voxels", 10)

        self.testBtn = self.addButton("Test Analysis", options, self.testAnalysis, 120)

        optionsFrame.setLayout(options)

        container.addWidget(optionsFrame)

    def updateUIAfterInput(self):
        self.modelBuilder.refresh()

    def launchWorkbench(self, cifti_output_path):
        try:
            views.workbench_launcher.launch(self.config, cifti_output_path)
        except:
            info = sys.exc_info()
            self.alert("Error opening workbench.\n%s\n%s" % (info[0], info[1]))
            print(info)

    def activateProgressBar(self):
        self.progress.show()
        self.progress.setMaximum(len(self.input.data()))
        self.progress.setValue(len(self.input.data()) / 2)

    def appendTextToOutputDisplay(self, txt):
        self.modelOutput.setText("%s\n%s" % (self.modelOutput.toPlainText(), txt))

        self.modelOutput.verticalScrollBar().setValue(self.modelOutput.verticalScrollBar().maximum())

    def onAnalysisProgressMessage(self, txt):

        self.appendTextToOutputDisplay(txt)

    def onAnalysisError(self, exception_info):
        # (exctype, value, traceback.format_exc())
        self.appendTextToOutputDisplay("Error! %s" % exception_info[1])

    def loadAnalysisModuleSpecific(self):
        """for overriding in subclasses"""
        if hasattr(self.analysis, "loaded_from_data"):
            saved_state = self.analysis.loaded_from_data

            self.model = self.analysis.model

            if hasattr(self.analysis, "model"):

                # self.open_mplus_model_raw(raw_mplus_model_text)
                # self.onSelectTemplate(self.analysis.template)
                self.hideTemplateChoiceDisplay()

                self.modelBuilder.loadAnalysis(self.analysis, self)
            else:
                if "template" in saved_state:
                    t = models.mplus_template.MplusTemplate(saved_state['template'])

                    self.onSelectTemplate(t)

            if "current_model" in saved_state:
                self.modelBuilder.generatedModelViewer.setText(saved_state["current_model"])

            if "output_dir" in saved_state:
                self.outputViewer.setOutputDir(saved_state["output_dir"])

            self.outputViewer.refreshBatches()

            self.modelBuilder.on_click_apply_template_variables()

            self.loadOutputParameterChoices()

    def runAnalysisBackgroundWorker(self, progress_callback, finished_callback, error_callback):

        self.mplus_output_contents = ""

        self.analysis.model = self.model  # todo this shouldn't be necessary, analysis.model should already be set but confirm
        self.analysis.title = self.title
        self.mplus_output_contents = self.analysis.go(self.input,
                                                      self.dataPreview.missing_tokens,
                                                      progress_callback=progress_callback,
                                                      error_callback=error_callback)

        # finished_callback.emit()  this is called when the worker completes automatically

        return "Done."

    def setExecuteButtonState(self, in_progress):
        self.cancelBtn.setEnabled(in_progress)
        self.runBtn.setEnabled(not in_progress)
        self.testBtn.setEnabled(not in_progress)

    def onAnalysisFinish(self):

        self.outputViewer.refreshBatches()

        self.setExecuteButtonState(False)

        self.appendTextToOutputDisplay("Analysis Complete")

        self.appendTextToOutputDisplay(self.mplus_output_contents)

        if hasattr(self, 'analysis'):
            cifti_output_path = self.analysis.cifti_output_path
        else:
            cifti_output_path = ""

        selected_outputs = self.analysis.output_parameters

        if len(selected_outputs) == 0:
            msg = "Analysis complete but no output fields were selected for extraction yet.  Go to the Output Selector tab and select the rows from the MPlus output that you would like aggregated and click Extract."
            self.appendTextToOutputDisplay(msg)
        else:

            # todo this might be redundant, probably already extracted
            self.outputViewer.extract()

            if len(cifti_output_path) > 0 and not self.cancelling:
                if self.chkAutoLaunchWorkbench.isChecked():

                    if hasattr(self, 'analysis'):
                        self.appendTextToOutputDisplay(
                            "Opening output file %s in Connectome Workbench" % cifti_output_path)

                        self.launchWorkbench(cifti_output_path)
                else:
                    self.appendTextToOutputDisplay(
                        "The output file %s is available for opening in Connectome Workbench" % cifti_output_path)

    def runAnalysis(self, limit_by_row=-1, limit_by_voxel=-1):

        self.cancelling = False
        self.analysis.cancelling = False

        self.setExecuteButtonState(True)

        if hasattr(self, "input"):
            self.input.cancelling = False

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.modelOutput.setText("Starting Analysis...")

        self.analysis.setBatchTitle(self.title)

        self.analysis.paths.create_new_batch()

        self.outputViewer.refreshBatches()

        self.model.title = self.analysis.batchTitle

        self.analysis.limit_by_row = limit_by_row
        self.analysis.limit_by_voxel = limit_by_voxel

        worker = Worker(self.runAnalysisBackgroundWorker)  # Any other args, kwargs are passed to the run function

        worker.signals.progress.connect(self.onAnalysisProgressMessage)
        worker.signals.finished.connect(self.onAnalysisFinish)
        worker.signals.error.connect(self.onAnalysisError)
        # Execute
        self.threadpool.start(worker)

    def testAnalysis(self):

        limit_by_row = -1
        limit_by_voxel = -1

        try:
            if self.checkLimitRows.isChecked():
                limit_by_row = int(self.wLimitRows.text())
        except:
            self.alert("Invalid value in the Limit By Row field.  Test not started.")
            return

        try:
            if self.checkLimitVoxels.isChecked():
                limit_by_voxel = int(self.wLimitVoxels.text())
        except:
            self.alert("Invalid value in the Limit By Voxel field.  Test not started.")
            return
        self.runAnalysis(limit_by_row, limit_by_voxel)

    def onSelectTemplate(self, template):

        self.template = template

        self.analysis.template = template

        raw_mplus_model_text = template.return_if_exists("rawmodel")

        self.open_mplus_model_raw(raw_mplus_model_text)

        self.hideTemplateChoiceDisplay()

        self.modelBuilder.loadAnalysis(self.analysis, self)

        # def closeEvent(self, event):
        # do stuff

    #        event.ignore()
    # if can_exit:
    #    event.accept()  # let the window close
    # else:
    #    event.ignore()

    def hideTemplateChoiceDisplay(self):
        [self.tabs.setTabEnabled(i, True) for i in range(1, self.tabs.count())]
        self.tabs.setTabEnabled(0, False)
        self.tabs.setStyleSheet(
            "QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")

    def addOutputParameter(self, key):
        self.analysis.output_parameters.append(key)
        self.loadOutputParameterChoices()
