from PyQt5 import QtWidgets, QtCore

from sour.usb_connection import find_usb_cameras
from sour.sony import SONYconn
import usb


class CameraConnection(QtWidgets.QDialog):

    camera_obj = QtCore.pyqtSignal(object, str)

    def __init__(self, parent=None):
        super(QtWidgets.QDialog, self).__init__(parent)
        self.camera_connected = False

        self.setWindowTitle('Camera Connections Parameters')

        cameras = list(find_usb_cameras())

        self.camera_dict = {}
        cameras_available = []

        for i in range(len(cameras)):

            name = 'Camera #'+str(int(i))
            camera_name = (
                cameras[i].manufacturer
                + ' '
                + cameras[i].product
            )
            
            cameras_available.append(camera_name)

            self.camera_dict[name] = {
                'Name' : camera_name,
                'Connection': cameras[i]
            }

        self.list_cameras_available_label = QtWidgets.QLabel('Cameras Found')
        self.list_cameras_available = QtWidgets.QComboBox()

        self.list_cameras_available.addItems(cameras_available)

        self.list_cameras_mode_label = QtWidgets.QLabel('Camera Mode')
        self.list_cameras_mode = QtWidgets.QComboBox()

        camera_modes = ['Remote', 'Media Transfer']

        self.list_cameras_mode.addItems(camera_modes)

        self.connect_camera_btn = QtWidgets.QPushButton('Connect To Camera')

        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.list_cameras_available_label, 0, 0)
        layout.addWidget(self.list_cameras_available, 0, 1)

        layout.addWidget(self.list_cameras_mode_label, 1, 0)
        layout.addWidget(self.list_cameras_mode, 1, 1)

        layout.addWidget(self.connect_camera_btn, 2, 1)

        self.connect_camera_btn.clicked.connect(self.connect_camera)
        self.connect_camera_btn.clicked.connect(self.close_dialog)

        self.setLayout(layout)

    def connect_camera(self):

        camera_chosen = self.list_cameras_available.currentText()
        mode_chosen = self.list_cameras_mode.currentText()

        if mode_chosen == 'Remote':
            mode = 'RemoteControl'
        elif mode_chosen == 'Media Transfer':
            mode = 'MediaTransfer'

        for i in self.camera_dict.keys():
            if self.camera_dict[i]['Name'] == camera_chosen:
                conn = self.camera_dict[i]['Connection']
            else:
                pass

        camera = SONYconn(
            name = camera_chosen,
            camera = conn
        )
        
        if isinstance(conn, usb.core.Device):
            self.camera_connected = True

        self.camera_obj.emit(camera, mode)

    def close_dialog(self):

        dialog = CameraStatus(self.camera_connected)
        dialog.exec_()

        self.close()

class CameraStatus(QtWidgets.QDialog):

    def __init__(self, status, parent=None):

        super(QtWidgets.QDialog, self).__init__(parent)

        if status:
            self.label = QtWidgets.QLabel('Camera Successfully Connected')
        else:
            self.label = QtWidgets.QLabel('Camera Not Connected')

        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.label, 0, 0)

        self.setLayout(layout)
