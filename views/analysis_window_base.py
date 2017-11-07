from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from models.input_spreadsheet import *


class AnalysisWindow(QWidget):
    NumButtons = ['Go']

    title = "Analysis Window"

    def __init__(self, config):
        super(AnalysisWindow, self).__init__()
        self.config = config
        font = QFont()
        font.setPointSize(16)
        self.initUIGeneral()
        self.initUISpecific()

    def initUIGeneral(self):
        self.center()
        self.setWindowTitle(self.title)

        grid = QGridLayout()
        self.grid = grid

        self.setLayout(grid)
        self.createVerticalGroupBox()

        self.analysisOptionsLayout = QVBoxLayout()
        self.analysisOptionsLayout.addWidget(self.verticalGroupBox)

        grid.addLayout(self.analysisOptionsLayout, 0, 0)

    def initUISpecific(self):
        # intended for overriding by subclasses
        print("override this method in the subclass for a particular kind of analysis")

    def open_input_file(self, path):
        try:
            self.input = InputSpreadsheet(path)

            self.render_dataframe(self.input._data)
        except:
            print("error")

    def render_dataframe(self, data):
        t = self.inputTable
        t.setColumnCount(len(data.columns))
        t.setRowCount(len(data.index))
        for i in range(len(data.index)):
            for j in range(len(data.columns)):
                t.setItem(i, j, QTableWidgetItem(str(data.iget_value(i, j))))

        for j in range(len(data.columns)):
            t.setHorizontalHeaderItem(j, QTableWidgetItem(data.columns[j]))

        t.show()

    def handle_open_action(self, filename):
        print("todo handle open file")

    def handle_save_action(self, filename):
        print("todo save")

    def createVerticalGroupBox(self):
        self.verticalGroupBox = QGroupBox()

        layout = QVBoxLayout()
        for i in self.NumButtons:
            button = QPushButton(i)
            button.setObjectName(i)
            layout.addWidget(button)
            layout.setSpacing(10)
            self.verticalGroupBox.setLayout(layout)
            button.clicked.connect(self.submitCommand)

    def submitCommand(self):
        eval('self.' + str(self.sender().objectName()) + '()')

    def plot3(self):
        self.draw_graph()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def width_needed_for_node(self, node, levels_to_go=0, single_node_width=150):
        # todo add memoization http://www.python-course.eu/python3_memoization.php
        spacer = 100
        if levels_to_go == 0:
            return single_node_width
        pred = self.g.predecessors(node)
        if len(pred) == 0:
            return single_node_width
        else:
            total = 0
            for n in pred:
                total += self.width_needed_for_node(n, levels_to_go - 1, 1.0 * single_node_width)
            total += (len(pred) - 1) * spacer
            return total

    def alert(self, txt):
        errorbox = QMessageBox()
        errorbox.setText(str(txt))
        errorbox.exec_()
