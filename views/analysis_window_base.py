from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from models import *
import glob
import os
from models import input_spreadsheet
from views.widgets.template_chooser_widget import *
import views.view_utilities as util


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
        self.showMaximized()
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
        # placeholder for subclasses to override if they need to handle a change in tabs.
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

        wb_command_prefix = self.config.getOptional("wb_command_path_prefix", "")
        if len(wb_command_prefix) > 0:
            self.input.wb_command_prefix = wb_command_prefix

        self.updateUIAfterInput()
        self.dataPreview.render_dataframe(self.input._data, path)
        if hasattr(self, "analysis"):
            self.analysis.input = self.input


            # except:
            #    self.alert("Error while opening file " + path)

    def validateConfiguration(self):
        config_problems = self.analysis.configValidationErrors()

        if len(config_problems) > 0:
            error_msg = "Your configuration file is missing some items that are required for the full functionality.\n"
            for problem in config_problems:
                # 2-tuples of key, description
                error_msg += "\t%s: %s\n" % problem

            error_msg += "\nPlease fix your configuration file %s" % self.config.path

            self.alert(error_msg)

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
        return util.addButton(caption, container, on_click, width)

    def save(self):
        if hasattr(self, 'savedFilePath') and len(self.savedFilePath) > 0:
            self.analysis.save(self.savedFilePath)
        else:
            savefile, ok = QFileDialog.getSaveFileName(self)
            self.analysis.save(savefile)
            self.savedFilePath = savefile
            self.config.addToRecentFileList(savefile)

    def open(self, file_contents, from_path):
        print("opening ")
        print(file_contents)
        self.savedFilePath = from_path
        self.handle_open(file_contents)
        self.handle_open_specifically(file_contents)

    def handle_open_specifically(self, file_contents):
        """for subclass overriding"""
        print("implement in subclass")

    def loadAnalysis(self, analysis):
        self.analysis = analysis
        if hasattr(analysis, "input_data_path"):
            self.open_input_file(analysis.input_data_path)
        self.loadAnalysisModuleSpecific()

        # todo load all attributes from saved file format

    def loadAnalysisModuleSpecific(self):
        """for overriding in subclasses"""
        print("override to map module specific attributes from saved data file")

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

    def addColumnNamesToListView(self, listView, columnNames):

        model = listView.model()

        model.clear()

        for col in columnNames:
            item = QStandardItem(col)
            # check = Qt.Checked if 1 == 1 else Qt.Unchecked
            # item.setCheckState(check)
            item.setCheckable(True)
            model.appendRow(item)

    def createColumnNameListWidget(self, single_selection=False):
        model = QStandardItemModel()

        view = QListView()

        view.setModel(model)

        if single_selection:
            # todo #bug this is not governing the checkbox-ing, just the row level selection. we want the
            # to restrict it to single checkbox selection
            view.setSelectionMode(QAbstractItemView.SingleSelection)

        return view
