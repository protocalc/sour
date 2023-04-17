from PyQt5 import QtWidgets, QtCore
import copy
import time

class TransferMediaTab(QtWidgets.QWidget):

    camera_connected_media_signal = QtCore.pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super(QtWidgets.QWidget, self).__init__(parent)

        if hasattr(self, 'camera_obj'):
            self.camera_obj.initialize_camera(mode = self.camera_mode)
            self.camera_connected = True
        else:
            self.camera_connected = False

        self.get_content_list()

        mainlayout = QtWidgets.QGridLayout(self)
        mainlayout.addWidget(self.FileTable, 0, 0, 1, 1)

    @QtCore.pyqtSlot(object, str)
    def get_camera(self, obj, string):
        self.camera_obj = copy.copy(obj)
        self.camera_mode = copy.copy(string)

        if self.camera_obj:
            self.camera_connected_media_signal.emit(True)

    def get_content_list(self):

        self.FileTable = QtWidgets.QTableWidget()
        self.FileTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.camera_connected_media_signal.connect(self.update_table)

    def update_table(self):

        if self.camera_mode == 'MediaTransfer':
            self.camera_obj.start_MTP_comms()

            time.sleep(1.5)

            self.all_files, files_count = self.camera_obj.get_files_info()

            count = 0

            self.btns = {}

            self.FileTable.setRowCount(files_count)
            self.FileTable.setColumnCount(2)
            self.FileTable.setHorizontalHeaderLabels(['File Name',''])

            for i in self.all_files.keys():
                for j in range(len(self.all_files[i]['Name'])):

                    self.FileTable.setItem(
                        count, 0, QtWidgets.QTableWidgetItem(self.all_files[i]['Name'][j])
                    )

                    self.btns[self.all_files[i]['Name'][j]] = QtWidgets.QPushButton('Download')

                    self.btns[self.all_files[i]['Name'][j]].clicked.connect(
                        lambda: self._download_single_file(
                            self.all_files[i]['Name'][j],
                            self.all_files[i]['FileCode'][j],
                            self.all_files[i]['DownloadCode'][j][:4]
                        )
                    )

                    self.FileTable.setCellWidget(
                        count, 1, self.btns[self.all_files[i]['Name'][j]]
                    )

                    count += 1

    def _download_single_file(self, file_name, file_code, file_download_code):

        self.camera_obj._transfer_large_files(file_name, file_code, file_download_code)
