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