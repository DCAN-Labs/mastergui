from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from models import *
import glob
import os
from models import input_spreadsheet
import views.view_utilities as util

from views.template_chooser_widget import *


class SplashWindow(QWidget):
    def __init__(self, parent_application_window):
        super(SplashWindow, self).__init__()
        self.parent_application_window = parent_application_window

        self.config = self.parent_application_window.config

        font = QFont()
        font.setPointSize(16)
        self.initUIGeneral()

    def initUIGeneral(self):
        self.setWindowTitle("Launch Screen")

        grid = QHBoxLayout()
        self.grid = grid

        self.setLayout(grid)

        self.recentLayout = QVBoxLayout()
        self.recentList = QListView()

        self.recentList.setModel(QStandardItemModel())

        f = QFont()
        f.setBold(True)

        l = QLabel("Recent Analyses")
        l.setFont(f)
        self.recentLayout.addWidget(l)

        self.recentLayout.addWidget(self.recentList)

        self.load_recent_files()

        recentWidget = QWidget()
        recentWidget.setLayout(self.recentLayout)

        util.addButton("Open", self.recentLayout, self.on_click_open)

        grid.addWidget(recentWidget, stretch=3)

        new_button_layout = QVBoxLayout()

        l = QLabel("Create Analysis")
        l.setFont(f)
        new_button_layout.addWidget(l)
        new_button_layout.setAlignment(Qt.AlignTop)
        for k, v in self.config.getOptional("analyzers", {}).items():
            util.addButton("New " + v.get("title", ""), new_button_layout, self.newClickHandler(k))

        new_button_widget = QWidget()
        new_button_widget.setLayout(new_button_layout)

        self.recentList.doubleClicked.connect(self.on_double_click)

        grid.addWidget(new_button_widget)

    def newClickHandler(self, module_name):
        return lambda: self.on_click_new(module_name)

    def on_double_click(self, a):
        try:
            row = a.row()

            if row == 0:  # the first row is an artificial entry, offering Browse, rather than coming from the actual list of recent files.
                self.parent_application_window.open_action()
            else:
                path = self.recentList.model().item(a.row()).text().strip()
                if len(path) > 0:
                    self.parent_application_window.open_file(path)
        except Exception as e:
            util.alert(str(e))

    def load_recent_files(self):
        path = self.config.getOptional("recent_files_path", "mastergui_recents")
        if os.path.exists(path):
            with open(path, 'r') as f:
                files = f.readlines()
                self.addColumnNamesToListView(self.recentList, files)

    def on_click_open(self, a):
        try:
            item = self.recentList.selectedIndexes()[0]

            if item.row() == 0:
                self.parent_application_window.open_action()
            else:
                path = self.recentList.model().item(item.row()).text().strip()
                self.parent_application_window.open_file(path)
        except Exception as e:
            util.alert(str(e))

    def on_click_new(self, module):
        try:
            self.parent_application_window.new_analysis(module)
        except Exception as e:
            util.alert(str(e))

    def addColumnNamesToListView(self, listView, columnNames):

        model = listView.model()

        model.clear()

        columnNames = ["<Browse>"] + columnNames
        for col in columnNames:
            item = QStandardItem(col)
            model.appendRow(item)

    def createColumnNameListWidget(self):
        model = QStandardItemModel()

        view = QListView()

        view.setModel(model)

        view.setSelectionMode(QAbstractItemView.SingleSelection)

        return view
