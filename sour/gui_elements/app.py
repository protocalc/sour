from PyQt5 import QtWidgets, QtCore

from sour.gui_elements.tabs.remote import RemoteTab
from sour.gui_elements.tabs.transfer import TransferMediaTab

from sour.gui_elements.dialogs.camera_connection import CameraConnection

import copy

class MainWindow(QtWidgets.QMainWindow):

    camera = QtCore.pyqtSignal(object, str)

    def __init__(self):
        super().__init__()
        self.title = 'SOny gUi Remote'

        self.setWindowTitle(self.title)
        
        menubar = self.menuBar()

        self.connect_menu = menubar.addMenu('Camera Connection')
        camera_connection = QtWidgets.QAction('Configuration', self)
        self.connect_menu.addAction(camera_connection)
        camera_connection.triggered.connect(self.camera_connection_menu)

        self.TabLayout = MainWindowTab()

        self.camera.connect(self.TabLayout.tab1.get_camera)
        self.camera.connect(self.TabLayout.tab2.get_camera)
        
        self.setCentralWidget(self.TabLayout)
        

    def camera_connection_menu(self):

        dialog = CameraConnection()
        dialog.camera_obj.connect(self.get_camera_obj)
        dialog.exec_()

        self.camera.emit(self.camera_obj, self.camera_mode)

    @QtCore.pyqtSlot(object, str)
    def get_camera_obj(self, obj, string):

        self.camera_obj = copy.copy(obj)
        self.camera_mode = copy.copy(string)

        self.connect_camera()

    def connect_camera(self):
        if hasattr(self, 'camera_obj'):
            self.camera_obj.initialize_camera(ControlMode = self.camera_mode)

    def disconnect_camera(self):

        print('Test')
        if hasattr(self, 'camera_obj'):
            self.camera_obj._session_handler(ControlMode = self.camera_mode)
            print('Disconnected')
        

class MainWindowTab(QtWidgets.QTabWidget):

    '''
    Layout for the main tab window
    '''

    def __init__(self, parent = None):
        super(MainWindowTab, self).__init__(parent)

        self.tab1 = RemoteTab()
        self.tab2 = TransferMediaTab()

        self.addTab(self.tab1,"Remote Control")
        self.addTab(self.tab2,"Transfer Media")
