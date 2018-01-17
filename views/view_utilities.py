from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from models import *
import glob
import os
from models import input_spreadsheet
from views.template_chooser_widget import *



def addButton(caption, container, on_click, width=-1):
    button = QPushButton(caption)
    if width >= 0:
        button.setFixedWidth(width)

    button.setObjectName(caption)
    button.clicked.connect(on_click)
    container.addWidget(button)

    return button

def addColumnNamesToListView(listView, columnNames):

    model = listView.model()

    model.clear()

    for col in columnNames:
        item = QStandardItem(col)
        # check = Qt.Checked if 1 == 1 else Qt.Unchecked
        # item.setCheckState(check)
        item.setCheckable(True)
        model.appendRow(item)

def createColumnNameListWidget(single_selection=False):
    model = QStandardItemModel()

    view = QListView()

    view.setModel(model)

    if single_selection:
        # todo #bug this is not governing the checkbox-ing, just the row level selection. we want the
        # to restrict it to single checkbox selection
        view.setSelectionMode(QAbstractItemView.SingleSelection)

    return view

def alert(txt):
    errorbox = QMessageBox()
    errorbox.setText(str(txt))
    errorbox.exec_()

def selectedLabelsFromListView(list):

    m = list.model()
    labels = []
    for i in range(m.rowCount()):
        item = m.item(i)
        if item.checkState() == Qt.Checked:
            labels.append(item.text())

    return labels

def createBoldLabel(text):
    f = QFont()
    f.setBold(True)

    l = QLabel(text)
    l.setFont(f)

    return l