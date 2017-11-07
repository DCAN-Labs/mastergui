from views.main_window import *
from models import *

if __name__ == '__main__':

    app = QApplication(sys.argv)

    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = MasterGuiApp()
    screen.show()
    sys.exit(app.exec_())
