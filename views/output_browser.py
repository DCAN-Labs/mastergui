from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import glob
import os
import numpy as np
import views.view_utilities as util
from models import paths
from views.widgets.combobox import *

cifti_radio_button_index = 2

class OutputBrowserWidget(QWidget):
    def __init__(self, parentAnalysisWidget):
        super(OutputBrowserWidget, self).__init__()
        self.parentAnalysisWidget = parentAnalysisWidget
        self.selected_batch_name = ""
        self.last_selected_pattern_id = 0
        self.initUI()
        self.refreshing_batches = False

    def initUI(self):
        layout = QVBoxLayout()

        output_path_descriptor = [("label","Output Directory:") , ("line",), ("button","Change")]


        outputPathLayout, outputPathWidgets = util.createHLineFromTemplate(output_path_descriptor)

        change_output_path_button = outputPathWidgets[2]
        change_output_path_button.clicked.connect(self.on_click_change_output_path)

        self.outputDirWidget = outputPathWidgets[1]
        self.outputDirWidget.setEnabled(False)

        self.outputDirWidget.returnPressed.connect(self.on_click_refresh)
        self.outputDirWidget.setFixedWidth(500)


        self.batchDropDown = ComboBox(on_change = self.on_batch_row_changed)

        frm = QFormLayout()


        batchDeleteBtn = QPushButton("Delete Batch")
        batchDeleteBtn.clicked.connect(self.on_click_delete_batch)
        frm.addRow("Output Directory:",util.createHLineFromWidgets([self.outputDirWidget,change_output_path_button]) )

        frm.addRow("Batches:", util.createHLineFromWidgets([self.batchDropDown, batchDeleteBtn]))

        exploreLayout = QHBoxLayout()

        self.exploreLayout = exploreLayout

        frm.addRow(self.createRadioButtons())


        self.fileViewer = QTextEdit()
        self.fileViewer.setReadOnly(True)

        self.ciftiButtion = util.addButton("Open Cifti", self.groupWidget.layout(), self.on_click_opencifti)
        self.ciftiButtion.setVisible(False)

        self.fileListView = QListView()
        self.fileListView.setSelectionMode(QAbstractItemView.SingleSelection)

        exploreLayout.addWidget(self.fileListView, stretch=1)
        self.initDetailUI(exploreLayout)
        self.initDetailUISpecific(exploreLayout)

        layout.addLayout(frm)
        layout.addLayout(exploreLayout)

        pathLine = QHBoxLayout()
        self.pathWidget = QLineEdit()
        self.pathWidget.setReadOnly(True)
        pathLine.addWidget(QLabel("Path:"), stretch = 1 )
        pathLine.addWidget(self.pathWidget, stretch = 50)
        #make the path transparent background
        self.pathWidget.setStyleSheet("background-color:rgba(0,0,0,0);border:None")
        layout.addLayout(pathLine)
        self.setLayout(layout)

        self.pattern = ""


    def on_click_delete_batch(self):
        path = self.selected_batch_path
        prompt = "Are you SURE you want to delete the entire batch %s  (All mplus inputs, outputs, and generated results such as ciftis will be irrevocably deleted)?" % path
        choice = QMessageBox.question(self,"Delete?",prompt, QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            try:
                self.analysis.removeBatch(path)
            except:
                util.alert("Error attempting to remove batch.")
            self.refreshBatches()

    def on_click_change_output_path(self):

        path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if path:
            self.analysis.paths.root = path
            self.outputDirWidget.setText(path)
            self.refreshBatches()
            self.refreshFiles()

    def initDetailUI(self, exploreLayout):
        exploreLayout.addWidget(self.fileViewer, stretch=5)

    def initDetailUISpecific(self, exploreLayout):
        #for subclasses to override if necessary
        return

    def createRadioButtons(self):

        labels = ["Inputs", "Outputs", "Ciftis"]
        sep = os.path.sep
        suffix = sep + "*.*"

        self.patterns = [paths.INPUTS_DIRNAME + suffix,paths.OUTPUTS_DIRNAME + suffix, paths.CIFITS_DIRNAME + sep + "*.nii"]

        group = QButtonGroup()
        groupWidget = QWidget()
        layout = QHBoxLayout()

        self.patternLabel = QLabel("File Pattern:")

        layout.addWidget(self.patternLabel)


        idx = 0
        for i in range(len(labels)):
            label = labels[i]
            btn = QRadioButton(label)
            if i==1:
                btn.setChecked(True)

            group.addButton(btn, idx)
            layout.addWidget(btn)
            idx += 1



        groupWidget.setLayout(layout)
        #groupWidget.setFixedWidth(400)
        group.buttonClicked.connect(self.on_pattern_btn_clicked)
        self.patternButtonGroup = group

        self.patternWidget = QLineEdit("outputs/*.*")
        self.patternWidget.returnPressed.connect(self.on_click_refresh)
        layout.addWidget(self.patternWidget)
        button = util.addButton("Refesh", layout, self.on_click_refresh, 70)

        self.groupWidget = groupWidget

        return groupWidget

    def setOutputDir(self, path):
        self.outputDirWidget.setText(path)
        self.refreshBatches()
        self.refreshFiles()

    def on_pattern_btn_clicked(self, i):

        selected_id = i.group().checkedId()
        self.last_selected_pattern_id = selected_id
        pattern = self.patterns[selected_id]
        self.patternWidget.setText(pattern)

        self.ciftiButtion.setVisible(selected_id==cifti_radio_button_index)

        if selected_id == cifti_radio_button_index:
            if self.fileViewer.isVisible():
                self.fileViewer.setVisible(False)
        elif not self.fileViewer.isVisible():
            self.fileViewer.setVisible(True)

        #self.fileViewer.setVisible(selected_id != cifti_radio_button_index)

        self.on_click_refresh()


    def on_click_refresh(self):
        self.last_selected_path  = ""
        self.refreshFiles()
        self.refreshBatches()

    @property
    def selected_batch_path(self):
        return self.analysis.paths.path_for_batch_name(self.selected_batch_name)

    def refreshFiles(self):

        path = os.path.join(self.selected_batch_path, self.patternWidget.text())
        self.selected_file_context = os.path.split(path)[0]

        self.batch_context_path = path

        self.loadOutputFiles(path)

    def refreshBatches(self):
        if hasattr(self.parentAnalysisWidget,"analysis"):
            batches = self.parentAnalysisWidget.analysis.batches()
            self.batchDropDown.update(batches)

    def on_click_opencifti(self):
        if hasattr(self, "last_selected_path"):
            if len(self.last_selected_path)>0:
                self.parentAnalysisWidget.launchWorkbench(self.last_selected_path)

    def loadOutputFiles(self, path_pattern):
        self.last_selected_path = ""

        paths = glob.glob(path_pattern)

        model = QStandardItemModel()

        # todo possibly parameterize and/or change UI but loading 92k+ paths is not viable in the current model, hangs the UI
        max_paths_to_show = 100
        paths = paths[:max_paths_to_show]
        for p in paths:
            name = os.path.basename(p)
            item = QStandardItem(name)
            model.appendRow(item)

        self.fileListView.setModel(model)

        self.fileListView.selectionModel().currentChanged.connect(self.on_file_row_changed)

    def on_file_row_changed(self, current, previous):
        context = os.path.dirname(self.batch_context_path)
        path = os.path.join(context, current.data())

        self.pathWidget.setText(path)

        self.last_selected_path = path

        if not self.ciftiButtion.isVisible():

            with open(path, 'r') as f:
                contents = f.readlines()

            self.fileViewer.setText("".join(contents))

    def on_batch_row_changed(self, text):

        self.selected_batch_name = text

        self.pathWidget.setText(self.selected_batch_path)

        self.refreshFiles()

    def hidePatternSelector(self):
        self.groupWidget.setVisible(False)
