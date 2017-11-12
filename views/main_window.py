import sys
import os
from views.mplus_analysis_window import *
from models import config
from views import mplus_analysis_window


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
    def __init__(self, appClass=mplus_analysis_window.MplusAnalysisWindow, mdimode=False):
        super(MasterGuiApp, self).__init__()

        self.init_ui()
        self.mdimode = mdimode

        self.setGeometry(100, 100, 800, 600)
        # this automatic launch of the mplus analysis is just temporary
        # while there is only one analysis type available
        # to facillitate debugging
        self.load_config()
        self.analysis_class = appClass(self.config)

        self.new_mplus_analysis()

    def load_config(self):
        if hasattr(sys.modules['__main__'], "__file__"):
            rootdir = os.path.dirname(sys.modules['__main__'].__file__)
            config_path = os.path.join(rootdir, "config.yml")
            self.config = config.Config(config_path)
        else:
            print("config not available")

    def add_analysiswindow_as_subwindow(self, gw, title=""):
        sub = QMdiSubWindow()
        sub.setWidget(gw)
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
            self.handle_open_action(openfile)
        else:
            print("something not ok")

    def save_action(self):
        savefile, ok = QFileDialog.getSaveFileName(self)
        if savefile:
            self.handle_save_action(savefile)

    def handle_open_action(self, filename):

        if self.mdimode:
            # todo discern what window to send command to if any
            self.mdi.activeSubWindow().widget().handle_open_action(filename)
        else:
            # default is to hand it to the running window
            self.graphapp.handle_open_action(filename)

    def handle_save_action(self, filename):
        self.graphapp.handle_save_action(filename)

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
            ['&New', 'New Analysis', 'Ctrl+N', 'exit.png', self.new_mplus_analysis],
            ['&Open', 'Open', 'Ctrl+O', 'exit.png', self.open_action],
            ['&Save', 'Save', 'Ctrl+S', 'exit.png', self.save_action],
            ['&Exit', 'Exit Application', 'Ctrl+Q', 'exit.png', qApp.quit]
        ]

        for m in filemenu_metadata:
            fileMenu.addAction(self.menu_item(*m))

    def new_mplus_analysis(self):
        if self.mdimode:
            self.mdi = QMdiArea()
            self.mdi.setViewMode(1)  # tabbed = 1, 0 = regular child windows
            self.setCentralWidget(self.mdi)
            self.add_analysiswindow_as_subwindow(self.analysis_class, "Main Doc")
        else:
            self.setCentralWidget(self.analysis_class)

        filename = self.config._data.get("open_path_on_launch", "")
        if len(filename) > 0:
            if os.path.exists(filename):
                self.analysis_class.open_input_file(filename)
            else:
                self.alert(filename + " does not exist. Check your config.yml file attribute open_path_on_launch.")

        filename = self.config._data.get("open_mplus_model_on_launch", "")
        if len(filename) > 0:
            if os.path.exists(filename):
                self.analysis_class.open_mplus_model_template(filename)
            else:
                self.alert(
                    filename + " does not exist. Check your config.yml file attribute open_mplus_model_on_launch.")

    def alert(self, txt):
        errorbox = QMessageBox()
        errorbox.setText(str(txt))
        errorbox.exec_()

    def init_toolbars(self):
        mplusAction = QAction('Mplus', self)
        mplusAction.setShortcut('Ctrl+M')
        mplusAction.triggered.connect(self.new_mplus_analysis)

        self.analysistoolbar = self.addToolBar('analysis_toolbar')
        self.analysistoolbar.addAction(mplusAction)


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
