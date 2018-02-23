from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import glob
import os
import numpy as np
import views.view_utilities as util
from models import paths
from views.widgets.combobox import *

cifti_radio_button_index = 3

class OutputBrowserWidget(QWidget):
    def __init__(self, parentAnalysisWidget):
        super(OutputBrowserWidget, self).__init__()
        self.parentAnalysisWidget = parentAnalysisWidget
        self.last_selected_pattern_id = 0
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Analysis Output Directory:"))
        self.outputDirWidget = QLineEdit()
        self.outputDirWidget.returnPressed.connect(self.on_click_refresh)
        layout.addWidget(self.outputDirWidget)

        layout.addWidget(QLabel("Specific Batch Output Sub-Directory:"))
        self.batchDirWidget = QLineEdit()
        self.batchDirWidget.setReadOnly(True)
        layout.addWidget(self.batchDirWidget)

        self.batchDropDown = ComboBox(on_change = self.on_batch_row_changed)

        layout.addWidget(self.batchDropDown)

        self.patternLabel = QLabel("File Pattern:")

        layout.addWidget(self.patternLabel)

        exploreLayout = QHBoxLayout()

        self.exploreLayout = exploreLayout

        layout.addWidget(self.createRadioButtons())

        self.fileViewer = QTextEdit()
        self.fileViewer.setReadOnly(True)



        self.ciftiButtion = util.addButton("Open Cifti", layout, self.on_click_opencifti)
        self.ciftiButtion.setVisible(False)

        self.fileListView = QListView()
        self.fileListView.setSelectionMode(QAbstractItemView.SingleSelection)

        exploreLayout.addWidget(self.fileListView, stretch=1)
        self.initDetailUI(exploreLayout)
        self.initDetailUISpecific(exploreLayout)
        layout.addLayout(exploreLayout)

        self.setLayout(layout)

        self.output_dir = ""
        self.pattern = ""

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

        idx = 0
        for label in labels:
            btn = QRadioButton(label)

            group.addButton(btn, idx)
            layout.addWidget(btn)
            idx += 1

        groupWidget.setLayout(layout)
        #groupWidget.setFixedWidth(400)
        group.buttonClicked.connect(self.on_pattern_btn_clicked)
        self.patternButtonGroup = group

        self.patternWidget = QLineEdit()
        self.patternWidget.returnPressed.connect(self.on_click_refresh)
        layout.addWidget(self.patternWidget)
        button = util.addButton("Refesh", layout, self.on_click_refresh, 70)

        self.groupWidget = groupWidget

        return groupWidget

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

    def refreshFiles(self):

        path = os.path.join(self.parentAnalysisWidget.analysis.paths.current_batch_path, self.patternWidget.text())

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
        #self.output_dir = output_dir
        #self.pattern = pattern

        #self.outputDirWidget.setText(output_dir)
        #self.patternWidget.setText(pattern)
        # len(glob.glob(os.path.join(analysis.batchOutputDir, "*.inp.out")))

        paths = glob.glob(path_pattern)

        model = QStandardItemModel()

        templates = {}

        # todo possibly parameterize and/or change UI but loading 92k+ paths is not viable in the current model, hangs the UI
        max_paths_to_show = 100
        paths = paths[:100]
        for p in paths:
            name = os.path.basename(p)
            item = QStandardItem(name)
            model.appendRow(item)

        self.fileListView.setModel(model)

        self.fileListView.selectionModel().currentChanged.connect(self.on_file_row_changed)

    def on_file_row_changed(self, current, previous):
        context = os.path.dirname(self.batch_context_path)
        path = os.path.join(context, current.data())

        self.last_selected_path = path

        if not self.ciftiButtion.isVisible():

            with open(path, 'r') as f:
                contents = f.readlines()

            self.fileViewer.setText("".join(contents))

    def on_batch_row_changed(self, text):

        self.parentAnalysisWidget.analysis.paths.current_batch_name = text

        self.refreshFiles()

        #self.last_selected_path = path

        #if not self.ciftiButtion.isVisible():
        #    path = os.path.join(self.output_dir, current.data())

#            with open(path, 'r') as f:
#                contents = f.readlines()

#            self.fileViewer.setText("".join(contents))
    def hidePatternSelector(self):
        self.groupWidget.setVisible(False)
