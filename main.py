from views.mastergui_app import *
import sys

if __name__ == '__main__':

    app = QApplication(sys.argv)

    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))

    args = sys.argv[1:]  #grab the command line arguments except for the filename

    if len(args)>0:
        config_path = args[0]
    else:
        #if a custom config path has not been specified logic encapsulated inside the app
        #will look in a default location
        config_path = ""

    screen = MasterGuiApp(config_path)
    screen.show()
    sys.exit(app.exec_())
