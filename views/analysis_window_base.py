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
        self.tabs.currentChanged.connect(self.onTabChanged)

    def onTabChanged(self, p_int):
        #placeholder for subclasses to override if they need to handle a change in tabs.
        print("Tab changed %d" % p_int)

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
        self.dataPreview.render_dataframe(self.input._data, path)
        self.analysis.input = self.input

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

    def addButton(self, caption, container, on_click, width=-1):
        button = QPushButton(caption)
        if width >= 0:
            button.setFixedWidth(width)

        button.setObjectName(caption)
        button.clicked.connect(on_click)
        container.addWidget(button)

        return button

    def save(self):
        print("SAVE!")
        if hasattr(self,'savedFilePath') and len(self.savedFilePath)>0:
            print('save existing path')
        else:
            savefile, ok = QFileDialog.getSaveFileName(self)
            self.analysis.save(savefile)
            self.savedFilePath = savefile

    def open(self,file_contents, from_path):
        print("opening ")
        print(file_contents)
        self.savedFilePath = from_path
        self.handle_open(file_contents)

    def handle_open_specifically(self,file_contents):
        """for subclass overriding"""
        print("implement in subclass")

    def loadAnalysis(self, analysis):
        self.analysis = analysis

    def loadAnalysisSpecifics(self):
        print("override in subclass")

    def closeEvent(self, event):

        close_msg = "Save this analysis before closing?"
        reply = QMessageBox.question(self, 'Message',
                                           close_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.save()
            event.accept()
        elif reply == QMessageBox.Cancel:
            event.ignore()
        else:
            event.accept()