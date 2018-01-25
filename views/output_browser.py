from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import glob
import os
import numpy as np


class OutputBrowserWidget(QWidget):
    def __init__(self):
        super(OutputBrowserWidget, self).__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Output Directory:"))
        self.outputDirWidget = QLineEdit()
        self.outputDirWidget.returnPressed.connect(self.on_click_refresh)
        layout.addWidget(self.outputDirWidget)

        self.patternLabel = QLabel("File Pattern:")

        layout.addWidget(self.patternLabel)

        exploreLayout = QHBoxLayout()

        self.exploreLayout = exploreLayout

        layout.addWidget(self.createRadioButtons())
        self.patternWidget = QLineEdit()
        self.patternWidget.returnPressed.connect(self.on_click_refresh)
        layout.addWidget(self.patternWidget)

        self.fileViewer = QTextEdit()
        self.fileViewer.setReadOnly(True)

        button = QPushButton("Refresh")

        button.clicked.connect(self.on_click_refresh)
        layout.addWidget(button)
        button.setFixedWidth(70)
        self.listView = QListView()

        self.listView.setSelectionMode(QAbstractItemView.SingleSelection)

        exploreLayout.addWidget(self.listView, stretch=1)
        self.initDetailUI(exploreLayout)
        layout.addLayout(exploreLayout)

        self.setLayout(layout)

        self.output_dir = ""
        self.pattern = ""

    def initDetailUI(self, exploreLayout):
        exploreLayout.addWidget(self.fileViewer, stretch=5)

    def createRadioButtons(self):
        labels = ["CSVs", "Mplus Input Files", "Mplus Output Files"]
        self.patterns = ["*.csv", "*.inp", "*.out"]
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
        groupWidget.setFixedWidth(400)
        group.buttonClicked.connect(self.on_pattern_btn_clicked)
        self.patternButtonGroup = group
        self.groupWidget = groupWidget

        return groupWidget

    def on_pattern_btn_clicked(self, i):
        selected_id = i.group().checkedId()
        pattern = self.patterns[selected_id]
        self.patternWidget.setText(pattern)
        self.on_click_refresh()

    def on_click_refresh(self):

        self.loadOutputFiles(self.outputDirWidget.text(), self.patternWidget.text())

    def loadOutputFiles(self, output_dir, pattern):
        self.output_dir = output_dir
        self.pattern = pattern

        self.outputDirWidget.setText(output_dir)
        self.patternWidget.setText(pattern)
        # len(glob.glob(os.path.join(analysis.batchOutputDir, "*.inp.out")))

        paths = glob.glob(os.path.join(output_dir, pattern))

        model = QStandardItemModel()

        templates = {}

        # todo possibly parameterize and/or change UI but loading 92k+ paths is not viable in the current model, hangs the UI
        max_paths_to_show = 100
        paths = paths[:100]
        for p in paths:
            name = os.path.basename(p)
            item = QStandardItem(name)
            model.appendRow(item)

        self.listView.setModel(model)

        self.listView.selectionModel().currentChanged.connect(self.on_row_changed)

    def on_row_changed(self, current, previous):
        path = os.path.join(self.output_dir, current.data())

        with open(path, 'r') as f:
            contents = f.readlines()

        self.fileViewer.setText("".join(contents))

    def hidePatternSelector(self):
        self.groupWidget.setVisible(False)
