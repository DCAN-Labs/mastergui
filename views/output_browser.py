from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import glob
import os
import numpy as np



class OutputBrowserWidget(QWidget):
    def __init__(self):
        super(OutputBrowserWidget, self).__init__()

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Output Directory:"))
        self.outputDirWidget = QLineEdit()
        self.outputDirWidget.returnPressed.connect(self.on_click_refresh)
        layout.addWidget(self.outputDirWidget)

        layout.addWidget(QLabel("File Pattern:"))

        layout.addWidget(self.createRadioButtons())
        self.patternWidget = QLineEdit()
        self.patternWidget.returnPressed.connect(self.on_click_refresh)
        layout.addWidget(self.patternWidget)

        self.fileViewer = QTextEdit()
        self.fileViewer.setReadOnly(True)
        layout.addWidget(self.fileViewer)


        button = QPushButton("Refresh")

        button.clicked.connect(self.on_click_refresh)
        layout.addWidget(button)

        self.listView = QListView()

        self.listView.setSelectionMode(QAbstractItemView.SingleSelection)


        layout.addWidget(self.listView)

        self.setLayout(layout)

        self.output_dir = ""
        self.pattern = ""

    def createRadioButtons(self):
        labels = ["CSVs","Mplus Input Files","Mplus Output Files"]
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
        group.buttonClicked.connect(self.on_pattern_btn_clicked)
        self.patternButtonGroup = group
        return groupWidget

    def on_pattern_btn_clicked(self,i):
        selected_id = i.group().checkedId()
        pattern = self.patterns[selected_id]
        self.patternWidget.setText(pattern)
        self.on_click_refresh()

    def on_click_refresh(self):

        self.loadOutputFiles(self.outputDirWidget.text(), self.patternWidget.text())

    def loadOutputFiles(self,output_dir, pattern):
        self.output_dir = output_dir
        self.pattern = pattern

        self.outputDirWidget.setText(output_dir)
        self.patternWidget.setText(pattern)
        # len(glob.glob(os.path.join(analysis.batchOutputDir, "*.inp.out")))

        paths = glob.glob(os.path.join(output_dir, pattern))

        model = QStandardItemModel()

        templates = {}

        for p in paths:

            item = QStandardItem(p)
            model.appendRow(item)


        self.listView.setModel(model)

        self.listView.selectionModel().currentChanged.connect(self.on_row_changed)

    def on_row_changed(self, current, previous):
        path = current.data()

        with open(path,'r') as f:
            contents = f.readlines()

        self.fileViewer.setText("".join(contents))