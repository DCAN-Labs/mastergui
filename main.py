from views.main_window import *
import logging

if __name__ == '__main__':
    formatter_str = '%(levelname)s:%(asctime)s %(message)s'
    logging.basicConfig(filename='mastergui.log', filemode='w', level=logging.DEBUG, format=formatter_str,
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    # add log messages to console output too
    ch = logging.StreamHandler()
    root_logger = logging.getLogger()
    root_logger.addHandler(ch)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(formatter_str)
    ch.setFormatter(formatter)

    app = QApplication(sys.argv)

    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = MasterGuiApp()
    screen.show()
    sys.exit(app.exec_())
