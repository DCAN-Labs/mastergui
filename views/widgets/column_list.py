from PyQt5.QtWidgets import *
from views.widgets.addremove_buttonbar import *

class ColumnList(QWidget):
    """displays a list with a title above and a add/remove buttons at the bottom of it,
    generally used for displaying columns of non-imaging data"""

    def __init__(self, caption):
        """
        :param caption: displays as a bold title heading over the list
        """
        super(ColumnList, self).__init__()
        self.caption = caption
        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()

        layout.addWidget(createBoldLabel(self.caption))
        model = QStandardItemModel()

        list = QListView()
        list.setModel(model)
        self.columnListWidget = list


        layout.addWidget(list)

        self.setLayout(layout)

        self.buttonBar = AddRemoveButtonBar(self.on_click_add, self.on_click_remove)

        layout.addWidget(self.buttonBar)

    def setAddClickHandler(self, handler):
        self.buttonBar.setAddClickHandler(handler)

    def setRemoveClickHandler(self, handler):
        self.buttonBar.setRemoveClickHandler(handler)

    def on_click_add(self):
        print("add")

    def on_click_remove(self):
        print("remove")

    def loadValues(self, values):

        self.refreshList(values)

    def refreshList(self, columnNames):

        model = self.columnListWidget.model()

        model.clear()

        for col in columnNames:
            item = QStandardItem(col)
            # check = Qt.Checked if 1 == 1 else Qt.Unchecked
            # item.setCheckState(check)
            item.setCheckable(True)
            model.appendRow(item)

    def selectedRow(self):
        m = self.columnListWidget.model()
        idx = self.columnListWidget.selectedIndexes()
        if len(idx)>0:
            return m.itemFromIndex(idx[0]).text()

        return None