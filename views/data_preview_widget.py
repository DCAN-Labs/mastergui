from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import numpy as np


class DataPreviewWidget(QWidget):
    def __init__(self):
        super(DataPreviewWidget, self).__init__()

        self.default_missing_tokens_list = ["-888", "-888.0", "NA", ".", "", "nan"]

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Missing Data Tokens:"))
        self.missingDataTokens = QLineEdit()
        self.missingDataTokens.setText(",".join(self.default_missing_tokens_list))
        layout.addWidget(self.missingDataTokens)
        self.highlightMissing = QCheckBox("Highlight Missing Values")
        self.highlightMissing.setChecked(True)

        self.highlightMissing.stateChanged.connect(self.clickHighlighting)
        layout.addWidget(self.highlightMissing)
        self.inputTable = QTableWidget()

        layout.addWidget(self.inputTable)

        self.setLayout(layout)

    def clickHighlighting(self):
        self.render_dataframe(self.data)

    def table(self):
        return self.inputTable

    @property
    def missing_tokens(self):
        return self.missingDataTokens.text().split(",")

    def render_dataframe(self, data):

        self.data = data

        t = self.inputTable
        t.setColumnCount(len(data.columns))

        highlight_missing = self.highlightMissing.isChecked()

        # we will insert some computed rows at the top of the table
        computed_row_count = 3

        t.setRowCount(len(data.index) + computed_row_count)

        missing_tokens = self.missing_tokens

        # missing_color = QColor(252,187,161)
        missing_color = QColor(254, 224, 210)

        missingCountByCol = {}
        for i in range(len(data.index)):
            row_idx = i + computed_row_count
            t.setVerticalHeaderItem(row_idx, QTableWidgetItem(""))
            for j in range(len(data.columns)):
                v = data.iat[i, j]

                t.setItem(row_idx, j, QTableWidgetItem(str(v)))
                if str(v) in missing_tokens:
                    missingCountByCol[j] = missingCountByCol.get(j, 0) + 1
                    if highlight_missing:
                        t.item(row_idx, j).setBackground(missing_color)
        max_row_idx = 0
        min_row_idx = 1
        missing_idx = 2

        t.setVerticalHeaderItem(max_row_idx, QTableWidgetItem("Max Value:"))
        t.setVerticalHeaderItem(min_row_idx, QTableWidgetItem("Min Value:"))
        t.setVerticalHeaderItem(missing_idx, QTableWidgetItem("% Missing:"))

        f = QFont()
        f.setBold(True)
        # t.verticalHeader().setFont(f)

        for j in range(len(data.columns)):
            t.setHorizontalHeaderItem(j, QTableWidgetItem(data.columns[j]))
            # self.summaryTable.setHorizontalHeaderItem(j, QTableWidgetItem(data.columns[j]))
            col_data = data[data.columns[j]]
            print(col_data.name + str(col_data.dtype))
            #            try:
            if col_data.dtype == np.float64 or col_data.dtype == np.int64:
                col_max = np.max(col_data)
                col_min = np.min(col_data)
                # todo just hardcoding a missing value for the moment, adjust to recognize all
                n_missing = len(np.where(col_data == -888)[0])

                t.setItem(max_row_idx, j, QTableWidgetItem(str(col_max)))
                t.setItem(min_row_idx, j, QTableWidgetItem(str(col_min)))
            else:
                t.setItem(max_row_idx, j, QTableWidgetItem(""))
                t.setItem(min_row_idx, j, QTableWidgetItem(""))
            missing_for_col = missingCountByCol.get(j, 0)
            if len(data.index) > 0:
                percent_missing = str(100 * missing_for_col / len(data.index)) + "%"
                t.setItem(missing_idx, j, QTableWidgetItem(percent_missing))
            # self.summaryTable.item(max_row_idx,j).setStylesheet("color:red")
            # you can set colors from RGB values with QColor(r,g,b)
            t.item(max_row_idx, j).setBackground(Qt.gray)
            t.item(min_row_idx, j).setBackground(Qt.gray)
            t.item(missing_idx, j).setBackground(Qt.gray)

            #        except:
            #            print("math error")
        t.show()
