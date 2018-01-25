from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import glob
import json
import models
import views.view_utilities as util


class TemplateChooserWidget(QWidget):
    def __init__(self, path_to_templates, parent, display_elements=[]):
        super(TemplateChooserWidget, self).__init__()
        # path_to_templates = self.config._data["analyzers"][self.analyzerName]['templates']
        self.parent = parent

        if len(display_elements) == 0:
            # default set
            display_elements = [("Description", "description"), ("Inputs", "input"), ("Outputs", "output"),
                                ("Instructions", "instructions"), ("Example", "example"),
                                ("Raw Model File", "rawmodel")]

        self.display_elements = display_elements
        overallLayout = QVBoxLayout()

        layout = QHBoxLayout()

        template_paths = glob.glob(os.path.join(path_to_templates, "*.json"))

        model = QStandardItemModel()

        templates = {}

        for p in template_paths:

            # template_info = json.load(f, strict=False)
            try:
                template = models.mplus_template.MplusTemplate(p)
            except Exception as e:

                util.alert("Error opening template %s\n%s" % (p, str(e)))

                continue

            while template.name in templates:
                template.name += "[DupName]"

            item = QStandardItem(template.name)
            model.appendRow(item)

            templates[template.name] = template

        self.templates = templates

        view = QListView()

        view.setModel(model)

        view.setSelectionMode(QAbstractItemView.SingleSelection)

        self.templateViewer = QTextEdit()
        self.templateViewer.setReadOnly(True)

        # self.templateViewer = self.createTemplateViewer()

        self.listView = view

        layout.addWidget(view)
        layout.addWidget(self.templateViewer)

        topWidget = QWidget()
        topWidget.setLayout(layout)

        overallLayout.addWidget(topWidget)

        overallLayout.setAlignment(Qt.AlignRight)

        button = QPushButton("Select Template")
        button.setObjectName("Select Template")
        overallLayout.addWidget(button, 0, Qt.AlignRight)

        button.setFixedWidth(140)

        button.clicked.connect(self.selectAndContinue)

        self.setLayout(overallLayout)

        view.selectionModel().currentChanged.connect(self.on_row_changed)

        if len(template_paths) > 0:
            view.setCurrentIndex(model.index(0, 0))

    def selectAndContinue(self):

        self.parent.onSelectTemplate(self.activeTemplate)

    def createTemplateViewer(self):
        w = QWidget()
        w.setMaximumHeight(500)

        self.descDisplay = QTextEdit()
        self.descDisplay.setReadOnly(True)
        # self.descDisplay.setMaximumHeight(300)

        layout = QVBoxLayout()

        layout.addWidget(self.descDisplay)

        # displayWidgets = {}
        # captionWidgets = {}


        # for field in self.display_elements:
        #     key = field[1]
        #
        #     caption = QLabel(field[0])
        #     captionWidgets[key] = caption
        #     layout.addWidget(caption)
        #
        #     fieldWidget = QTextEdit()
        #     layout.addWidget(fieldWidget)
        #     displayWidgets[key] = fieldWidget

        # self.displayWidgets = displayWidgets
        # self.captionWidgets = captionWidgets



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

        text = ""
        for field in self.display_elements:
            key = field[1]
            txt = template.return_if_exists(key)
            # w = self.displayWidgets[key]
            # w.setText(txt)
            # caption = self.captionWidgets[key]
            if len(txt) > 0:
                # w.hide()
                # caption.hide()
                # else:
                text += "<H3>%s</H3>\n%s\n\n" % (key.title(), txt)
                # caption.show()
                # w.show()

        self.templateViewer.setText(text)
        # todo make this more generic for reuse with other analyzers

        self.activeTemplate = template
