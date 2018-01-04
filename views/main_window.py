import sys
import os
from views.mplus.mplus_analysis_window import *
from views.palm.palm_analysis_window import *
from views.fconnanova.fconnanova_analysis_window import *
from views.analysis_window_base import *
from models import config
from models.analysis import *
from models.fconnanova_analysis import *
from models.mplus_analysis import *
from models.palm_analysis import  *
#from views import mplus_analysis_window
from views import other_analysis


# https://riverbankcomputing.com/pipermail/pyqt/2009-May/022961.html
def excepthook(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.

    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """

    notice = \
        """An unhandled exception occurred.\n""" \
        """Error information:\n%s:%s\n%s""" % \
        (excType, excValue, tracebackobj)

    errorbox = QMessageBox()
    errorbox.setText(str(notice))
    errorbox.exec_()


# global exception handler
# sys.excepthook = excepthook

class MasterGuiApp(QMainWindow):
    def __init__(self, mdimode=True):
        super(MasterGuiApp, self).__init__()

        self.init_ui()
        self.mdimode = mdimode

        self.setGeometry(100, 100, 1200, 1000)
        # this automatic launch of the mplus analysis is just temporary
        # while there is only one analysis type available
        # to facillitate debugging
        self.load_config()
        # self.analysis_class = appClass(self.config)
        # self.analysis_class = other_analysis.OtherAnalysisWindow(self.config)
        # self.new_mplus_analysis()

        if self.mdimode:
            self.mdi = QMdiArea()
            # self.mdi.setViewMode(1)  # tabbed = 1, 0 = regular child windows
            self.setCentralWidget(self.mdi)

    def load_config(self):
        if hasattr(sys.modules['__main__'], "__file__"):
            rootdir = os.path.dirname(sys.modules['__main__'].__file__)
            config_path = os.path.join(rootdir, "config.json")
            self.config = config.Config(config_path)
        else:
            print("config not available")

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
        self.mdi.activateNextSubWindow()

        sub.showMaximized()

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

            analysis = Analysis.load(openfile,self.config)

            if analysis is not None:
                if type(analysis) is MplusAnalysis:
                    self.new_mplus_analysis(analysis)


    def save_action(self):

        active = self.activeAnalysisWindow()
        if active is not None:
            active.save()

    def activeAnalysisWindow(self):
        win = self.mdi.activeSubWindow()
        if win is not None:
            for w in win.children():
                if isinstance(w,AnalysisWindow):
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

    def new_mplus_analysis(self, analysis = None):

        analysis_window = MplusAnalysisWindow(self.config)

        if analysis is not None:
            analysis_window.loadAnalysis(analysis)

        self.displayNewAnalysis(analysis_window)

    def new_palm_analysis(self):

        analysis = PalmAnalysisWindow(self.config)

        self.displayNewAnalysis(analysis)


    def new_fconnanova_analysis(self):

        analysis = FconnanovaAnalysisWindow(self.config)

        self.displayNewAnalysis(analysis)

    def displayNewAnalysis(self,analysis):
        if self.mdimode:
            self.add_analysiswindow_as_subwindow(analysis)
        else:
            self.setCentralWidget(analysis)

    def alert(self, txt):
        errorbox = QMessageBox()
        errorbox.setText(str(txt))
        errorbox.exec_()

    def init_toolbars(self):
        mplusAction = QAction('Mplus', self)
        mplusAction.setShortcut('Ctrl+M')
        mplusAction.triggered.connect(self.on_click_new_mplus_analysis)

        palmAction = QAction('Palm Analysis', self)
        palmAction.setShortcut('Ctrl+P')
        palmAction.triggered.connect(self.new_palm_analysis)

        fconnanovaAction = QAction('FCONNANOVA Analysis', self)
        fconnanovaAction.setShortcut('Ctrl+F')
        fconnanovaAction.triggered.connect(self.new_fconnanova_analysis)

        self.analysistoolbar = self.addToolBar('analysis_toolbar')
        self.analysistoolbar.addAction(mplusAction)
        self.analysistoolbar.addAction(palmAction)
        self.analysistoolbar.addAction(fconnanovaAction)


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
