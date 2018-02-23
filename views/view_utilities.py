from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from models import *
import glob
import os
from models import input_spreadsheet



def addButton(caption, container, on_click = None, width=-1, height = -1):
    """simple helper method to add a PyQt button
    with the most common settings

    caption: the text to appear in the button
    container: the QWidget or QLayout to which the new button should be added at the end
    on_click: (optional) a callback method to be called upon click
    width: if provided sets a fixed width, otherwise (default -1) lets PyQT
    determine the optimal width
    height: if provided sets a fixed height, otherwise (default -1) lets PyQT
    determine the optimal height

    """
    button = QPushButton(caption)

    button.setObjectName(caption)

    if on_click:
        button.clicked.connect(on_click)

    if width >= 0:
        button.setFixedWidth(width)

    if height >= 0:
        button.setFixedHeight(height)

    container.addWidget(button)

    return button

def addColumnNamesToListView(listView, columnNames, checkable = True):

    model = listView.model()

    model.clear()

    for col in columnNames:
        item = QStandardItem(col)
        # check = Qt.Checked if 1 == 1 else Qt.Unchecked
        # item.setCheckState(check)
        if checkable:
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

def boldQFont():
    f = QFont()
    f.setBold(True)
    return f

def createBoldLabel(text):

    f = boldQFont()
    l = QLabel(text)
    l.setFont(f)
    #l.setAutoFillBackground(True)
    return l

def addBoldLabel(text, container):
    l = createBoldLabel(text)
    container.addWidget(l)