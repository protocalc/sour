
from PyQt5 import QtWidgets
import sys

import sour.gui_elements.app as mainwindow



def main():
    app = QtWidgets.QApplication(sys.argv)

    ex = mainwindow.MainWindow()

    app.aboutToQuit.connect(ex.TabLayout.tab1.exit_threads_on_close)
    app.aboutToQuit.connect(ex.disconnect_camera)


    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
