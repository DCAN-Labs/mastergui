from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import glob
import json
import models


class TemplateChooserWidget(QWidget):
    def __init__(self, path_to_templates, display_elements=[]):
        super(TemplateChooserWidget, self).__init__()
        # path_to_templates = self.config._data["analyzers"][self.analyzerName]['templates']

        if len(display_elements) == 0:
            # default set
            display_elements = [("Description", "description"), ("Inputs", "input"), ("Outputs", "output"),
                                ("Instructions", "instructions"), ("Example", "example"),
                                ("Raw Model File", "rawmodel")]

        self.display_elements = display_elements

        layout = QHBoxLayout()

        template_paths = glob.glob(os.path.join(path_to_templates, "*.json"))

        model = QStandardItemModel()

        templates = {}
        for p in template_paths:

            # template_info = json.load(f, strict=False)
            template = models.mplus_template.MplusTemplate(p)

            while template.name in templates:
                template.name += "[DupName]"

            item = QStandardItem(template.name)
            model.appendRow(item)

            templates[template.name] = template

        self.templates = templates

        view = QListView()

        view.setModel(model)

        view.setSelectionMode(QAbstractItemView.SingleSelection)

        self.templateViewer = self.createTemplateViewer()

        self.listView = view

        layout.addWidget(view)
        layout.addWidget(self.templateViewer)

        self.setLayout(layout)

        view.selectionModel().currentChanged.connect(self.on_row_changed)

    def createTemplateViewer(self):
        w = QWidget()
        layout = QVBoxLayout()

        displayWidgets = {}
        captionWidgets = {}

        for field in self.display_elements:
            key = field[1]

            caption = QLabel(field[0])
            captionWidgets[key] = caption
            layout.addWidget(caption)

            fieldWidget = QTextEdit()
            # fieldWidget.setTextBackgroundColor(Qt.color)
            # fieldWidget.setStyleSheet("background-color:red")
            layout.addWidget(fieldWidget)
            displayWidgets[key] = fieldWidget

        self.displayWidgets = displayWidgets
        self.captionWidgets = captionWidgets

        w.setLayout(layout)

        return w

    def on_row_changed(self, current, previous):
        print(current.data())
        print('Row %d selected' % current.row())

        template_key = current.data()
        if template_key in self.templates:
            template = self.templates[template_key]
            self.renderTemplate(template)
        else:
            print("Error template no longer stored")

    def renderTemplate(self, template):
        for field in self.display_elements:
            key = field[1]
            txt = template.return_if_exists(key)
            w = self.displayWidgets[key]
            w.setText(txt)
            caption = self.captionWidgets[key]
            if len(txt) == 0:
                w.hide()
                caption.hide()
            else:
                caption.show()
                w.show()
