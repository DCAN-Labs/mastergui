from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import glob
import os
import numpy as np
from views.view_utilities import *

from views.widgets.column_chooser import *

class PalmReaderOptions(QWidget):
    def __init__(self, parentAnalysisWindow):
        super(PalmReaderOptions, self).__init__()
        # AnalysisType
        # *'NumFactors'* -- an required scalar for between subject and combined ANOVAs
        #  specifies the number of between subject factors.
        # *'LevelsPerFactor'* -- a required M by 1 vector for between subject and
        #  combined ANOVAs, where M is the number of between subject factors. Each
        #  number specifies the number of levels per factor (e.g. three groups
        #  would be three levels).
        # *'NumRepeatedMeasures'* -- a required scalar for within subject repeated
        #  measures. Specifies the number of repeated measures per subject. All
        #  subjects must have all repeated measures.
        # *'Groups'* -- a N by M vector where N is the number of cases, and M is the
        #  number of between subject factors. Lists the assignment of each case to
        #  each factor. Required for between subject and combined ANOVAs. If the
        #  number of unique values does not equal the specified factor level, an
        #  error will occur.
        # *'SaveOutput'* -- a string that represents the full path to the output
        # directory. The program will save the design files in that directory.
        # *'RegressorVector'* -- a vector denoting which columns in Groups are
        # actually continuous variables. Only used if "regression" is selected. If
        # left unspecified, all columns in groups are assumed to be regressors.
        # Regressors will be automatically mean-centered, in case one forgot to do
        # so.

        self.parentAnalysisWindow = parentAnalysisWindow
        params = [("NumFactors","scalar"),("LevelsPerFactor","vector"),
         ("NumRepeatedMeasures","scalar"),("Groups","vector"),
         ("SaveOuput","string"),("RegressorVector","vector")]


        layout = QVBoxLayout()

        analysis_type_group_buttons = self.createRadioButtons()


        paramWidgets = {}

        self.formGroupBox = QGroupBox("Parameters")
        form_layout = QFormLayout()

        form_layout.addRow(QLabel("AnalysisType"), analysis_type_group_buttons)

        for p in params:
            param_type = p[1]
            if param_type=="vector":
                w = QTextEdit()
            elif param_type == "scalar":
                w= QSpinBox()
            else:
                w = QLineEdit()
            paramWidgets[p[0]] = w
            form_layout.addRow(QLabel(p[0]),w)

        self.formGroupBox.setLayout(form_layout)

        columnChooser = addButton("Add Categorical Variable",layout,self.test_column_chooser)
        columnChooser2 = addButton("Add Scalar Variable", layout, self.test_column_chooser)
        layout.addWidget(self.formGroupBox)
        self.setLayout(layout)

        self.output_dir = ""
        self.pattern = ""

    def test_column_chooser(self):

        if hasattr(self.parentAnalysisWindow,"input"):
            x = ColumnChooser(self.parentAnalysisWindow, self.parentAnalysisWindow.dataPreview)
            x.setWindowModality(Qt.WindowModal)
            x.show()
            x.exec_()

    def createRadioButtons(self):
        #comments from PalmReader.m 1/3/18
        #                   1) 'one_sample_test' -- use this when comparing a
        #                   single group against zero -- useful for
        #                   analyses on high-level statistics (e.g. paired t-tests).
        #                   2) 'two_sample_test' -- a comparison of means between
        #                   two groups. Make sure to specify the group assignments
        #                   using the 'Groups' parameter.
        #                   3) 'anova' -- a between subjects ANOVA only. Uses a GLM
        #                   to estimate mixed effects from the GLM, which
        #                   simplifies mathematically to an analysis of variance.
        #                   Consult with the fsl documentation for the proof. Make
        #                   sure that the 'Groups' parameter is set to include the
        #                   right number of factors with the right number of
        #                   levels. Will also need to specify 'NumFactors', and
        #                   'LevelsPerFactor'
        #                   4) 'rmanova' -- a mixed effects GLM that assumes the
        #                   covariance between all repeated measures is roughly
        #                   equal. The parameter 'NumRepeatedMeasures' must be specified.
        #                   One can specify a combined analysis by including the
        #                   following three parameters: 'Groups','NumFactors',
        #                   'LevelsPerFactor'. Otherwise, this will be a fully
        #                   within subject design.



        labels = ["one_sample_test","two_sample_test","anova", "rmanova"]

        self.patterns = ["*.csv", "*.inp", "*.out"]

        group = QButtonGroup()
        groupWidget = QWidget()
        layout = QHBoxLayout()

        idx = 0
        for label in labels:
            btn = QRadioButton(label)

            group.addButton(btn, idx)
            layout.addWidget(btn)
            idx += 1

        groupWidget.setLayout(layout)

        self.analysisTypeGroup = group
        return groupWidget
