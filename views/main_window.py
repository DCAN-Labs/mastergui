import sys
import os
from views.mplus.mplus_analysis_window import *
from views.palm.palm_analysis_window import *
from views.fconnanova.fconnanova_analysis_window import *
from views.analysis_window_base import *
from views.splash_window import *
from views.view_utilities import *
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
    def __init__(self):
        super(MasterGuiApp, self).__init__()

        self.load_config()

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

        #self.splash.showMinimized()
        analysis = Analysis.load(openfile, self.config)

        if analysis is not None:
            if type(analysis) is MplusAnalysis:
                self.new_mplus_analysis(analysis)
        self.addToRecentFileList(openfile)

    def addToRecentFileList(self, path):
        recents_path = self.config.getOptional("recent_files_path", "mastergui_recents")

        if os.path.exists(recents_path):
            with open(recents_path, 'r') as f:
                files = f.readlines()
                files.insert(0,path)

                unique_tracker = {}
                unique_files = []
                for p in files:
                    p = p.strip()
                    if len(p)>0:
                        if not p in unique_tracker:
                            unique_files.append(p)
                            unique_tracker[p] = True
        else:
            unique_files = [path]


        with open(recents_path, 'w') as f:
            f.writelines("\n".join(unique_files))


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

        self.add_analysiswindow_as_subwindow(analysis)

    def alert(self, txt):
        errorbox = QMessageBox()
        errorbox.setText(str(txt))
        errorbox.exec_()

    def init_toolbars(self):

        self.analysistoolbar = self.addToolBar('analysis_toolbar')

        for k,v in self.config.getOptional("analyzers", {}).items():
            action = QAction(v.get("title","(missing analyzer title in config"),self)
            shortcut = v.get("shortcut","")
            if len(shortcut)>0:
                action.setShortcut(shortcut)
            action.triggered.connect(self.newClickHandler(k))
            self.analysistoolbar.addAction(action)


    def newClickHandler(self,module_name):
        return lambda:self.new_analysis(module_name)

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
