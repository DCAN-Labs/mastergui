from views.main_window import *
import logging
import os
if __name__ == '__main__':
    formatter_str = '%(levelname)s:%(asctime)s %(message)s'
    #todo: better logging destination
    mastergui_log_path = os.path.expanduser("mastergui.log")
    logging.basicConfig(filename=mastergui_log_path, filemode='w', level=logging.DEBUG, format=formatter_str,
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
