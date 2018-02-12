from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from views.view_utilities import *

class AddRemoveButtonBar(QGroupBox):
    """a ui widget containing side by side + and - buttons
    for adding and removing from an associated list"""
    def __init__(self, on_click_add = None, on_click_remove = None):
        """
        optionally provide event handler callbacks to be called
        when the user clicks the respective button
        :param on_click_add:
        :param on_click_remove:
        """
        super(AddRemoveButtonBar, self).__init__()

        buttonLayout = QHBoxLayout()

        button_side_length = 25

        self.btnAdd = addButton("+", buttonLayout, on_click_add, button_side_length, button_side_length)

        self.btnRemove = addButton("-", buttonLayout, on_click_remove, button_side_length, button_side_length )

        buttonLayout.setContentsMargins(0,0,0,0)
        self.setLayout(buttonLayout)
        self.setAutoFillBackground(True)


    def setAddClickHandler(self, handler):
        self.btnAdd.clicked.connect(handler)

    def setRemoveClickHandler(self, handler):
        self.btnRemove.clicked.connect(handler)