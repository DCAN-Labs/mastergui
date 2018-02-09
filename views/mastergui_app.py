import sys
import os
import logging

from views.mplus.mplus_analysis_window import *
from views.palm.palm_analysis_window import *
from views.fconnanova.fconnanova_analysis_window import *
from views.analysis_window_base import *
from views.splash_window import *
import views.view_utilities as util
from models import config
from models.analysis import *
from models.fconnanova_analysis import *
from models.mplus_analysis import *
from models.palm_analysis import *
# from views import mplus_analysis_window
from views import other_analysis
import traceback


def init_logging(config):
    formatter_str = '%(levelname)s:%(asctime)s %(message)s'

    mastergui_log_path = config["log_path"]

    logging.basicConfig(filename=mastergui_log_path, filemode='w', level=logging.DEBUG, format=formatter_str,
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    # add log messages to console output too
    ch = logging.StreamHandler()
    root_logger = logging.getLogger()
    root_logger.addHandler(ch)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(formatter_str)
    ch.setFormatter(formatter)


#extra "ugly" error messages with diagnostics info that ultimately we won't want to subject
#end users to but are useful during development

debug_mode = True
# https://riverbankcomputing.com/pipermail/pyqt/2009-May/022961.html
def excepthook(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.

    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """

    log_notice = "".join(traceback.format_exception(excType, excValue, tracebackobj))

    if debug_mode:
        user_facing_notice = log_notice
    else:
        user_facing_notice = \
            """An unexpected error occurred.\n""" \
            """Error information:\n%s:%s""" % \
            (excType, excValue)

    logging.error("Globally unhandled error occurred:" + log_notice)

    errorbox = QMessageBox()
    errorbox.setText(user_facing_notice)
    errorbox.exec_()

# global exception handler, usually disabled during development but should be enabled in production
#sys.excepthook = excepthook


class MasterGuiApp(QMainWindow):
    def __init__(self, optional_path_to_config_file=""):
        super(MasterGuiApp, self).__init__()

        try:
            self.load_config(optional_path_to_config_file)

            init_logging(self.config)

            self.init_ui()

            self.setGeometry(100, 100, 1200, 1000)

            self.mdi = QMdiArea()

            self.setCentralWidget(self.mdi)

            self.splash = SplashWindow(self)

            sub = QMdiSubWindow()
            sub.setWidget(self.splash)
            self.mdi.addSubWindow(sub)
            self.mdi.activateNextSubWindow()

            self.splashSubWindow = sub

            sub.showMaximized()
        except Exception as e:
            util.alert(str(e))
            raise e

    def load_config(self, config_path=""):

        self.config = config.Config(config_path)

    def add_analysiswindow_as_subwindow(self, gw):

        sub = QMdiSubWindow()
        sub.setWidget(gw)

        if hasattr(gw, 'title'):
            title = gw.title
        else:
            title = "MPlus Analysis"

        if len(title) > 0:
            sub.setWindowTitle(title)

        self.mdi.addSubWindow(sub)

        self.splashSubWindow.showMinimized()

        sub.show()

        self.mdi.setActiveSubWindow(sub)

        aw = self.mdi.activeSubWindow()
        self.mdi.cascadeSubWindows()

    def init_ui(self):
        self.init_menus()
        self.init_toolbars()

    def closeWindow(self, appwindow):
        success = appwindow.close()
        if success:
            self.openwindows.remove(appwindow)
        if len(self.openwindows) > 0:
            # todo manage a reasonable stack of the last focused windows instead of just grabbing one
            self.setCentralWidget(self.openwindows[0])

    def open_action(self):
        openfile, ok = QFileDialog.getOpenFileName(self)

        if openfile:
            self.open_file(openfile)

    def open_file(self, openfile):

        # self.splash.showMinimized()
        analysis = Analysis.load(openfile, self.config)

        if analysis is not None:
            if type(analysis) is MplusAnalysis:
                self.new_mplus_analysis(analysis)
        self.addToRecentFileList(openfile)

    def addToRecentFileList(self, path):
        self.config.addToRecentFileList(path)

    def save_action(self):
        active = self.activeAnalysisWindow()
        if active is not None:
            active.save()

    def activeAnalysisWindow(self):
        win = self.mdi.activeSubWindow()
        if win is not None:
            for w in win.children():
                if isinstance(w, AnalysisWindow):
                    return w
        else:
            return None

    def menu_item(self, caption, statustip, shortcut, icon, connected_method):
        action = QAction(QIcon(icon), caption, self)
        # exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        action.setShortcut(shortcut)
        action.setStatusTip(statustip)
        action.triggered.connect(connected_method)
        return action

    def init_menus(self):
        # http://zetcode.com/gui/pyqt5/menustoolbars/

        self.statusBar()
        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&File')
        self.fileMenu = fileMenu
        self.menuBar().setNativeMenuBar(False)

        filemenu_metadata = [
            ['&New', 'New Analysis', 'Ctrl+N', 'exit.png', self.on_click_new_mplus_analysis],
            ['&Open', 'Open', 'Ctrl+O', 'exit.png', self.open_action],
            ['&Save', 'Save', 'Ctrl+S', 'exit.png', self.save_action],
            ['&Exit', 'Exit Application', 'Ctrl+Q', 'exit.png', qApp.quit]
        ]

        for m in filemenu_metadata:
            fileMenu.addAction(self.menu_item(*m))

    def on_click_new_mplus_analysis(self):
        self.new_mplus_analysis()

    def new_mplus_analysis(self, analysis=None):
        #optional variable analysis.  if an existing analysis model instance is not provided,
        #a new one will be created for you withing the MplusAnalysisWindow
        analysis_window = MplusAnalysisWindow(self.config, analysis)

        self.displayNewAnalysis(analysis_window)

    def new_palm_analysis(self):

        analysis = PalmAnalysisWindow(self.config)

        self.displayNewAnalysis(analysis)

    def new_fconnanova_analysis(self):

        analysis = FconnanovaAnalysisWindow(self.config)

        self.displayNewAnalysis(analysis)

    def displayNewAnalysis(self, analysis):

        self.add_analysiswindow_as_subwindow(analysis)

    def alert(self, txt):
        errorbox = QMessageBox()
        errorbox.setText(str(txt))
        errorbox.exec_()

    def init_toolbars(self):

        self.analysistoolbar = self.addToolBar('analysis_toolbar')

        for k, v in self.config.getOptional("analyzers", {}).items():
            action = QAction(v.get("title", "(missing analyzer title in config"), self)
            shortcut = v.get("shortcut", "")
            if len(shortcut) > 0:
                action.setShortcut(shortcut)
            action.triggered.connect(self.newClickHandler(k))
            self.analysistoolbar.addAction(action)

    def newClickHandler(self, module_name):
        return lambda: self.new_analysis(module_name)

    def new_analysis(self, module_name):
        if module_name == "mplus":
            analysis = MplusAnalysisWindow(self.config)
        elif module_name == "palm":
            analysis = PalmAnalysisWindow(self.config)
        elif module_name == "fconnanova":
            analysis = FconnanovaAnalysisWindow(self.config)
        else:
            self.alert("Unrecognized module name %s" % module_name)
            return

        self.displayNewAnalysis(analysis)


"""
Modify base on:
http://stackoverflow.com/questions/36086361/embed-matplotlib-in-pyqt-with-multiple-plot/36093604

"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = MasterGuiApp()
    screen.show()
    sys.exit(app.exec_())
