from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from views.analysis_window_base import *
from views.widgets.data_preview_widget import *
from views.output_browser import *
from views.palm.palm_reader_options import *
import views.workbench_launcher
import models
import datetime
import sys
import threading
import traceback
import time
from views.workers import *

class PalmAnalysisWindow(AnalysisWindow):
    def __init__(self, config):

        self.title = "Palm Analysis"
        self.analyzerName = "palm"
        super(PalmAnalysisWindow, self).__init__(config)

        a = models.palm_analysis.PalmAnalysis(self.config)

        missing_keys = a.missingRequiredConfigKeys()

        if len(missing_keys) > 0:
            self.alert(
                "Your configuration file is missing some items that are required for the full functionality.  Please provide the following keys: " + " ".join(
                    missing_keys))

    def openDataFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Data File", "",
                                                  "All Data Files (*.csv *.xls *.xlsx);;Excel Files (*.xls *.xlsx);;CSV files (*.csv)",
                                                  options=options)
        if fileName:
            self.fileName = fileName
            self.open_input_file(fileName)

    def initUISpecific(self):
        """
        This method is invoked by the base class upon initial loading and should contain the GUI
        initialization code specific to this particular analysis module
        :return:
        """

        self.dataPreview = DataPreviewWidget(self)

        self.initExecAnalysisWidget()

        self.palmReaderOptions = PalmReaderOptions(self)

        self.addTab(self.dataPreview, "Input Data Review")
        self.addTab(self.palmReaderOptions, "PalmReader Options")
        self.addTab(self.execAnalysisWidget, "Execution Tab")

        self.outputViewer = OutputBrowserWidget(self)
        self.addTab(self.outputViewer, "Output")
        self.tabs.setCurrentIndex(0)

        self.progress = QProgressBar()

    def initExecAnalysisWidget(self):
        self.execAnalysisWidget = QWidget()
        self.modelOutput = QTextEdit()

        l = QVBoxLayout()

        command_bar = QHBoxLayout()

        self.addButton("Run Analysis", command_bar, self.runAnalysis, 100)

        self.chkAutoLaunchWorkbench = QCheckBox("Launch Workbench When Complete")
        self.chkAutoLaunchWorkbench.setChecked(True)
        command_bar.addWidget(self.chkAutoLaunchWorkbench)

        self.initTestAnalysisFrame(command_bar)

        l.addLayout(command_bar)
        l.addWidget(self.modelOutput)

        self.execAnalysisWidget.setLayout(l)

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

        self.addButton("Test Analysis", options, self.testAnalysis, 120)

        optionsFrame.setLayout(options)

        container.addWidget(optionsFrame)

    def updateUIAfterInput(self):
        print("updateUIAfterInput")
        # stub
        True

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

    def runAnalysisBackgroundWorker(self, progress_callback, finished_callback, error_callback):

        mappings = self.dataPreview.selected_voxelized_columns()

        self.mplus_output_contents = ""
        self.mplus_output_contents = self.analysis.go(self.model, self.title, self.input,
                                                      self.dataPreview.missing_tokens, halt_after_n,
                                                      path_to_voxel_mappings=mappings,
                                                      progress_callback=progress_callback,
                                                      error_callback=error_callback)

        # finished_callback.emit()  this is called when the worker completes automatically

        return "Done."

    def onAnalysisFinish(self):
        self.appendTextToOutputDisplay("Analysis Complete")

        self.appendTextToOutputDisplay(self.mplus_output_contents)

        if hasattr(self, 'analysis'):
            cifti_output_path = self.analysis.cifti_output_path
        else:
            cifti_output_path = ""

        if len(cifti_output_path) > 0:
            if self.chkAutoLaunchWorkbench.isChecked():

                if hasattr(self, 'analysis'):
                    self.appendTextToOutputDisplay("Opening output file %s in Connectome Workbench" % cifti_output_path)

                    self.launchWorkbench(cifti_output_path)
            else:
                self.appendTextToOutputDisplay(
                    "The output file %s is available for opening in Connectome Workbench" % cifti_output_path)

    def runAnalysis(self, limit_by_row=-1, limit_by_voxel=-1):
        if False:
            self.threadpool = QThreadPool()
            print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

            # self.updateGeneratedMPlusInputFile()  #this probably shouldn't be here

            self.modelOutput.setText("Starting Analysis...")

            self.analysis = models.mplus_analysis.MplusAnalysis(self.config)

            self.analysis.setBatchTitle(self.title)

            self.model.title = self.analysis.batchTitle

            worker = Worker(self.runAnalysisBackgroundWorker)  # Any other args, kwargs are passed to the run function

            worker.signals.progress.connect(self.onAnalysisProgressMessage)
            worker.signals.finished.connect(self.onAnalysisFinish)
            worker.signals.error.connect(self.onAnalysisError)
            # Execute
            self.threadpool.start(worker)

    def testAnalysis(self):
        if False:

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
