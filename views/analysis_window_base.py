from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from models import *
import glob
import os
from views.template_chooser_widget import *
from models import input_spreadsheet


class AnalysisWindow(QWidget):
    NumButtons = ['Next']

    title = "Analysis Window"

    def __init__(self, config):
        super(AnalysisWindow, self).__init__()
        self.config = config
        font = QFont()
        font.setPointSize(16)
        self.initUIGeneral()
        self.initUISpecific()

    def initUIGeneral(self):
        self.setWindowTitle(self.title)

        grid = QGridLayout()
        self.grid = grid

        self.setLayout(grid)
        self.createVerticalGroupBox()

        self.initTabs()


    def initTabs(self):
        self.tabs = QTabWidget()
        self.grid.addWidget(self.tabs)
        self.tabs.show()

    def addTab(self, widget, title):
        self.tabs.addTab(widget, title)

    def initUISpecific(self):
        # intended for overriding by subclasses
        print("override this method in the subclass for a particular kind of analysis")

    def initModelSelection(self):

        path_to_templates = ""
        if self.analyzerName in self.config._data["analyzers"]:
            configData = self.config._data["analyzers"][self.analyzerName]
            if 'templates' in configData:
                path_to_templates = self.config._data["analyzers"][self.analyzerName]['templates']

        self.templateChooser = TemplateChooserWidget(path_to_templates, self)

        self.addTab(self.templateChooser, "Template Selection")

    def open_input_file(self, path):
        # try:
        self.input = input_spreadsheet.InputSpreadsheet(path)
        self.updateUIAfterInput()
        self.dataPreview.render_dataframe(self.input._data)
        # except:
        #    self.alert("Error while opening file " + path)

    def updateUIAfterInput(self):
        print("override in subclasses")

    def handle_open_action(self, filename):
        print("todo handle open file")

    def handle_save_action(self, filename):
        print("todo save")

    def createVerticalGroupBox(self):
        self.verticalGroupBox = QGroupBox()

        layout = QHBoxLayout()

        # button = QPushButton("Next")
        # button.setObjectName("Next")
        #        layout.addWidget(button)
        #       layout.setSpacing(10)
        self.verticalGroupBox.setLayout(layout)
        # button.clicked.connect(self.submitCommand)
        # self.btnNext = button
        # button.setEnabled(False)

    def submitCommand(self):
        eval('self.' + str(self.sender().objectName()) + '()')

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def alert(self, txt):
        errorbox = QMessageBox()
        errorbox.setText(str(txt))
        errorbox.exec_()
