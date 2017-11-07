from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from views.analysis_window_base import *
import os
import models


class MplusAnalysisWindow(AnalysisWindow):
    def __init__(self, config):
        self.default_missing_tokens_list = ["-888", "NA", "", "nan"]
        self.title = "Mplus Analysis"
        super(MplusAnalysisWindow, self).__init__(config)

    def open_mplus_model_template(self, path):
        self.model = models.mplus_model.MplusModel(path)
        self.modelTemplateViewer.setText(str(self.model._raw))

    def initUISpecific(self):
        self.analysisOptionsLayout.addWidget(QLabel("Missing Data Tokens:"))
        self.missingDataTokens = QLineEdit()
        self.missingDataTokens.setText(",".join(self.default_missing_tokens_list))
        self.analysisOptionsLayout.addWidget(self.missingDataTokens)

        self.modelTemplateViewer = QTextEdit()
        self.generatedModelViewer = QTextEdit()
        self.inputTable = QTableWidget()

        self.tabs = QTabWidget()

        x = QWidget()

        self.modelDesignContainer = QVBoxLayout()
        self.modelDesignContainer.addWidget(self.generatedModelViewer)
        x.setLayout(self.modelDesignContainer)
        self.tabs.resize(300, 200)
        self.tabs.addTab(self.inputTable, "Input Data Review")
        self.tabs.addTab(self.modelTemplateViewer, "Model Template")
        self.tabs.addTab(x, "New Mplus Model")
        self.grid.addWidget(self.tabs)

    def Go(self):
        # make data file with characters replaced
        output_path = os.path.join(self.config._data.get("output_dir", ""), "GENERATEDmissing.csv")
        self.input.save_cleaned_data(output_path, self.default_missing_tokens_list)
        # make mplus analysi file
        self.alert(output_path + " successfully saved.")
        # launch mplus
