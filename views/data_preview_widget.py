from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import numpy as np

voxel_mapping_idx = 0
max_row_idx = 1
min_row_idx = 2
missing_idx = 3
include_col_idx = 4


class DataPreviewWidget(QWidget):
    def __init__(self):
        super(DataPreviewWidget, self).__init__()

        self.default_missing_tokens_list = ["-888", "-888.0", "NA", ".", "", "nan"]

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Non-imaging Data File:"))
        self.filePathWidget = QLineEdit()
        layout.addWidget(self.filePathWidget)

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

        self.voxelized_columns = []

    def clickHighlighting(self):
        self.render_dataframe(self.data)

    def table(self):
        return self.inputTable

    def addVoxelColumn(self, path_col_index, colname="VOXEL"):

        insert_where = self.inputTable.columnCount()

        #self.inputTable.insertColumn(insert_where)

        #self.inputTable.setHorizontalHeaderItem(insert_where, QTableWidgetItem(colname))

        #self.setupComputedCellsForCol(insert_where)

        #self.inputTable.item(include_col_idx, insert_where).setCheckState(Qt.Checked)

        source_name = self.inputTable.horizontalHeaderItem(path_col_index).text()

        # copy the % missing from the source column
        #self.inputTable.item(missing_idx, insert_where).setText(
        #    self.inputTable.item(missing_idx, path_col_index).text())

        item = QTableWidgetItem(colname)
        item.setBackground(Qt.gray)
        self.inputTable.setItem(voxel_mapping_idx, path_col_index,  item)


        # store tuples of column mapping for later usage when generating data.
        self.voxelized_columns.append((source_name, colname))

    def selected_voxelized_columns(self):
        #or for each column in grid see if the voxelized row is set and selected.
        result = []
        for c in range(self.inputTable.columnCount()):
            item = self.inputTable.item(include_col_idx, c)
            if item.checkState() == Qt.Checked:
                mapped_value = self.getVoxelizedColumnName(c)

                if len(mapped_value)>0:
                    source_name = self.inputTable.horizontalHeaderItem(c).text()
                    result.append((source_name, mapped_value))

        return result

    def update_selected_checks_from_analysis(self, model):
        for v in model.using_variables:
            self.selectColumn(v)

    def selectColumn(self, col_name):
        for c in range(self.inputTable.columnCount()):

            header_col_name = self.inputTable.horizontalHeaderItem(c).text()
            mapped_col_name = self.getVoxelizedColumnName(c)
            if header_col_name == col_name or mapped_col_name == col_name:
                item = self.inputTable.item(include_col_idx, c)
                item.setCheckState(Qt.Checked)

    def getVoxelizedColumnName(self, col):
        return self.inputTable.item(voxel_mapping_idx, col).text()

    def possibleColumnNames(self):
        result = []
        for c in range(self.inputTable.columnCount()):
            any_mapped_name = self.getVoxelizedColumnName(c)
            if len(any_mapped_name)>0:
                result.append(any_mapped_name)
            else:
                result.append(self.inputTable.horizontalHeaderItem(c).text())
        return result

    @property
    def missing_tokens(self):
        return self.missingDataTokens.text().split(",")

    def render_dataframe(self, data, path = ""):

        self.data = data
        self.filePathWidget.setText(path)
        t = self.inputTable
        t.setColumnCount(len(data.columns))

        highlight_missing = self.highlightMissing.isChecked()

        # we will insert some computed rows at the top of the table
        computed_row_count = 5

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



        t.setVerticalHeaderItem(voxel_mapping_idx, QTableWidgetItem("Transform to Voxel Column Name:"))
        t.setVerticalHeaderItem(max_row_idx, QTableWidgetItem("Max Value:"))
        t.setVerticalHeaderItem(min_row_idx, QTableWidgetItem("Min Value:"))
        t.setVerticalHeaderItem(missing_idx, QTableWidgetItem("% Missing:"))
        t.setVerticalHeaderItem(include_col_idx, QTableWidgetItem("Include In Model:"))

        f = QFont()
        f.setBold(True)
        # t.verticalHeader().setFont(f)

        for j in range(len(data.columns)):

            self.setupComputedCellsForCol(j)

            t.setHorizontalHeaderItem(j, QTableWidgetItem(data.columns[j]))
            # self.summaryTable.setHorizontalHeaderItem(j, QTableWidgetItem(data.columns[j]))
            col_data = data[data.columns[j]]

            if col_data.dtype == np.float64 or col_data.dtype == np.int64:
                col_max = np.max(col_data)
                col_min = np.min(col_data)
                # todo just hardcoding a missing value for the moment, adjust to recognize all
                n_missing = len(np.where(col_data == -888)[0])

                t.item(max_row_idx, j).setText(str(col_max))
                t.item(min_row_idx, j).setText(str(col_min))
                # t.setItem(max_row_idx, j, QTableWidgetItem(str(col_max)))
                # t.setItem(min_row_idx, j, QTableWidgetItem(str(col_min)))
            # else:
            #    t.setItem(max_row_idx, j, QTableWidgetItem(""))
            #    t.setItem(min_row_idx, j, QTableWidgetItem(""))
            missing_for_col = missingCountByCol.get(j, 0)
            if len(data.index) > 0:
                percent_missing = str(100 * missing_for_col / len(data.index)) + "%"
                # t.setItem(missing_idx, j, QTableWidgetItem(percent_missing))
                t.item(missing_idx, j).setText(percent_missing)

        self.autoVoxelize()
        t.show()

    def autoVoxelize(self):
        """by convention we will assume that any column names that start with "PATH_" are intended for voxelization
        """
        for c in range(self.inputTable.columnCount()):
            item = self.inputTable.item(include_col_idx,c)

            colname = self.inputTable.horizontalHeaderItem(c).text()
            if colname[0:5] == "PATH_":
                self.addVoxelColumn(c, "VOXEL_" + colname[5:])

    def setupComputedCellsForCol(self, col, max_val="", min_val="", missing_count=""):
        t = self.inputTable

        for row in (voxel_mapping_idx, max_row_idx, min_row_idx, missing_idx, include_col_idx):
            # you can set colors from RGB values with QColor(r,g,b)

            if row == include_col_idx:
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Unchecked)
            else:
                item = QTableWidgetItem()
            item.setBackground(Qt.gray)
            t.setItem(row, col, item)
            # t.item(row, col).setBackground(Qt.gray)
