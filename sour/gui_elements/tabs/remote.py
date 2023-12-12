from PyQt5 import QtWidgets, QtCore
import copy
import time
from queue import Queue
import pyqtgraph as pg
import numpy as np


class RemoteTab(QtWidgets.QWidget):
    camera_connected_signal = QtCore.pyqtSignal(bool)
    live_view_status = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super(QtWidgets.QWidget, self).__init__(parent)

        self.camera_queue = Queue()

        self.camera_count = 0

        self.camera_connected = False
        self.live_view_on = False

        self.threadpool = QtCore.QThreadPool()

        self.camera_params()
        self.live_view()

        self.shot_button = QtWidgets.QPushButton("Capture")

        self.shot_button.clicked.connect(self.shot)

        mainlayout = QtWidgets.QGridLayout(self)
        mainlayout.addWidget(self.CameraParams, 0, 0, 1, 1)
        mainlayout.addWidget(self.LiveView, 0, 1, 1, 2)
        mainlayout.addWidget(self.shot_button, 1, 2, 1, 1)

    @QtCore.pyqtSlot(object, str)
    def get_camera(self, obj, string):
        self.camera_obj = copy.copy(obj)
        self.camera_mode = copy.copy(string)

        if self.camera_obj:
            self.camera_connected_signal.emit(True)

    def __select_values_mode(self, d, mode):
        if mode == "Photo":
            return d["Photo"]
        else:
            if "Video" in list(d.keys()):
                return d["Video"]
            else:
                return d["Photo"]

    def camera_params(self):
        self.CameraParams = QtWidgets.QGroupBox("SONY Controls")

        layout = QtWidgets.QGridLayout()

        self.focus_modes_available_label = QtWidgets.QLabel("Focus Mode")
        self.focus_modes_available = QtWidgets.QComboBox()

        self.program_available_label = QtWidgets.QLabel("Program Mode")
        self.program_available = QtWidgets.QComboBox()

        self.iso_available_label = QtWidgets.QLabel("ISO")
        self.iso_available = QtWidgets.QComboBox()

        self.shutter_speed_available_label = QtWidgets.QLabel("Shutter Speed")
        self.shutter_speed_available = QtWidgets.QComboBox()

        self.focus_distance_label = QtWidgets.QLabel("Focus Distance")

        self.focus_distance_available = QtWidgets.QComboBox()
        self.focus_distance_available.addItems(["Further", "Closer"])

        self.focus_distance_step = QtWidgets.QLineEdit("# Steps")
        self.focus_command = QtWidgets.QPushButton("Send Focus Control")

        self.focus_distance_infinity_label = QtWidgets.QLabel(
            "Focus to Infinity"
        )
        self.focus_distance_infinity = QtWidgets.QCheckBox()

        layout.addWidget(self.program_available_label, 0, 0, 1, 1)
        layout.addWidget(self.program_available, 0, 1, 1, 1)

        layout.addWidget(self.focus_modes_available_label, 1, 0, 1, 1)
        layout.addWidget(self.focus_modes_available, 1, 1, 1, 1)

        layout.addWidget(self.iso_available_label, 2, 0, 1, 1)
        layout.addWidget(self.iso_available, 2, 1, 1, 1)

        layout.addWidget(self.shutter_speed_available_label, 3, 0, 1, 1)
        layout.addWidget(self.shutter_speed_available, 3, 1, 1, 1)

        layout.addWidget(self.focus_distance_label, 4, 0, 1, 1)
        layout.addWidget(self.focus_distance_available, 4, 1, 1, 1)
        layout.addWidget(self.focus_distance_step, 4, 2, 1, 1)

        layout.addWidget(self.focus_distance_infinity_label, 5, 1, 1, 1)
        layout.addWidget(self.focus_distance_infinity, 5, 2, 1, 1)

        layout.addWidget(self.focus_command, 6, 2, 1, 1)

        self.focus_distance_available.setEnabled(False)
        self.focus_distance_step.setEnabled(False)
        self.focus_distance_infinity.setEnabled(False)
        self.focus_command.setEnabled(False)

        self.camera_connected_signal.connect(self.update_values)
        self.camera_connected_signal.connect(self.start_messaging_thread)

        self.shutter_speed_available.activated[str].connect(
            self.update_shutter_speed
        )
        self.focus_modes_available.activated[str].connect(
            self.update_focus_mode
        )
        self.iso_available.activated[str].connect(self.update_iso)
        self.program_available.activated[str].connect(
            self.update_program_mode
        )

        self.focus_distance_infinity.toggled.connect(
            self.update_focus_distance_infinity
        )

        self.focus_command.clicked.connect(self.update_focus_distance)

        self.CameraParams.setLayout(layout)

    @QtCore.pyqtSlot(bool)
    def update_values(self, cam_conn):
        self.camera_connected = copy.copy(cam_conn)

        if self.camera_connected:
            count = 0
            while count < 3:
                self.camera_obj.get_camera_properties()
                time.sleep(0.1)
                props = copy.copy(self.camera_obj.camera_properties)
                count += 1

            current_program = props["ExposureProgramMode"]["CurrentValue"]

            if "photo" in current_program.lower():
                mode = "Photo"
            else:
                mode = "Video"

            program_available_list = self.__select_values_mode(
                props["ExposureProgramMode"]["AvailableValues"], mode
            )
            focus_modes_available_list = self.__select_values_mode(
                props["FocusMode"]["AvailableValues"], mode
            )
            iso_available_list = self.__select_values_mode(
                props["ISO"]["AvailableValues"], mode
            )
            shutter_speed_available_list = self.__select_values_mode(
                props["ShutterSpeed"]["AvailableValues"], mode
            )

        else:
            program_available_list = []
            focus_modes_available_list = []
            iso_available_list = []
            shutter_speed_available_list = []

        self.shutter_speed_available.addItems(shutter_speed_available_list)
        self.iso_available.addItems(iso_available_list)
        self.program_available.addItems(program_available_list)
        self.focus_modes_available.addItems(focus_modes_available_list)

        self.shutter_speed_available.setCurrentText(
            props["ShutterSpeed"]["CurrentValue"]
        )
        self.iso_available.setCurrentText(props["ISO"]["CurrentValue"])
        self.program_available.setCurrentText(
            props["ExposureProgramMode"]["CurrentValue"]
        )
        self.focus_modes_available.setCurrentText(
            props["FocusMode"]["CurrentValue"]
        )

        if props["FocusMode"]["CurrentValue"] == "MF":
            self.focus_distance_available.setEnabled(True)
            self.focus_distance_step.setEnabled(True)
            self.focus_distance_infinity.setEnabled(True)
            self.focus_command.setEnabled(True)

        if self.camera_connected:
            if self.camera_mode != "RemoteControl":
                self.program_available.setEnabled(False)
                self.focus_modes_available.setEnabled(False)
                self.iso_available.setEnabled(False)
                self.shutter_speed_available.setEnabled(False)

                self.focus_distance_available.setEnabled(False)
                self.focus_distance_step.setEnabled(False)
                self.focus_distance_infinity.setEnabled(False)
                self.focus_command.setEnabled(False)

    @QtCore.pyqtSlot(bool)
    def start_messaging_thread(self, cam_conn):
        if cam_conn:
            self.talker()

    def exit_threads_on_close(self):
        if hasattr(self, "msg_worker"):
            self._interrupt_thread()
            self.msg_worker.stop()

        if hasattr(self, "LVworker"):
            self.LVworker.stop()

    def update_iso(self):
        if self.camera_connected:
            cmd = ["ISO", self.iso_available.currentText()]

            worker = Queuer(cmd, self.camera_queue, 0.05)

            worker.signals.completed.connect(self.complete)
            worker.signals.started.connect(self.start)
            self.threadpool.start(worker)

    def update_program_mode(self):
        if self.camera_connected:
            cmd = ["Program Mode", self.program_available.currentText()]

            worker = Queuer(cmd, self.camera_queue, 0.05)

            worker.signals.completed.connect(self.complete)
            worker.signals.started.connect(self.start)
            self.threadpool.start(worker)

    def update_focus_mode(self):
        if self.camera_connected:
            cmd = ["Focus Mode", self.focus_modes_available.currentText()]

            if cmd[1] == "MF":
                self.focus_distance_available.setEnabled(True)
                self.focus_distance_step.setEnabled(True)
                self.focus_distance_infinity.setEnabled(True)
                self.focus_command.setEnabled(True)
            else:
                self.focus_distance_available.setEnabled(False)
                self.focus_distance_step.setEnabled(False)
                self.focus_distance_infinity.setEnabled(False)
                self.focus_command.setEnabled(False)

            worker = Queuer(cmd, self.camera_queue, 0.05)

            worker.signals.completed.connect(self.complete)
            worker.signals.started.connect(self.start)
            self.threadpool.start(worker)

    def update_shutter_speed(self):
        if self.camera_connected:
            cmd = [
                "Shutter Speed",
                self.shutter_speed_available.currentText(),
            ]

            worker = Queuer(cmd, self.camera_queue, 0.05)

            worker.signals.completed.connect(self.complete)
            worker.signals.started.connect(self.start)
            self.threadpool.start(worker)

    def update_focus_distance(self):
        if self.camera_connected:
            cmd = [
                "Focus Distance",
                self.focus_distance_available.currentText(),
                int(self.focus_distance_step.text()),
            ]

            worker = Queuer(cmd, self.camera_queue, 0.05)

            worker.signals.completed.connect(self.complete)
            worker.signals.started.connect(self.start)
            self.threadpool.start(worker)

    def update_focus_distance_infinity(self):
        if self.camera_connected:
            if self.focus_distance_infinity.isChecked():
                self.focus_distance_available.setEnabled(False)
                self.focus_distance_step.setEnabled(False)
                self.focus_command.setEnabled(False)

                cmd = ["Focus Distance", "Infinity"]

                worker = Queuer(cmd, self.camera_queue, 0.05)

                worker.signals.completed.connect(self.complete)
                worker.signals.started.connect(self.start)
                self.threadpool.start(worker)

            else:
                self.focus_distance_available.setEnabled(True)
                self.focus_distance_step.setEnabled(True)
                self.focus_command.setEnabled(True)

    def complete(self):
        print("Added cmd to the Queue")

    def start(self):
        print("Adding cmd to the Queue")

    def talker(self):
        self.msg_thread = QtCore.QThread()
        self.msg_worker = Sender(self.camera_queue, self.camera_obj)

        self.msg_worker.moveToThread(self.msg_thread)

        self.msg_thread.started.connect(self.msg_worker.run)
        self.msg_worker.finished.connect(self._interrupt_thread)

        self.msg_worker.image.connect(self.update_image)

        self.msg_worker.cmd_start.connect(self.cmd_dialog)
        self.msg_worker.cmd_end.connect(self.close_dialog)

        self.msg_thread.start()

    @QtCore.pyqtSlot(list)
    def cmd_dialog(self, msg):
        flag = copy.copy(msg[0])
        param = copy.copy(msg[1])

        if flag:
            self.dialog = CommandStatus(param)
            self.dialog.exec_()

    @QtCore.pyqtSlot(bool)
    def close_dialog(self, flag):
        flag = copy.copy(flag)
        print("Test", flag)
        if flag:
            if hasattr(self, "dialog"):
                self.dialog.close()

    def _interrupt_thread(self):
        self.msg_thread.quit()

    @QtCore.pyqtSlot(np.ndarray)
    def update_image(self, array):
        self.image = copy.copy(array)

        if self.live_view_on:
            self.imageViewer.setImage(self.image)

    def shot(self):
        if self.camera_connected:
            if self.live_view_on:
                self.LiveViewButtonOFF.click()

            cmd = ["Capture", 0]

            worker = Queuer(cmd, self.camera_queue, 0.5)

            worker.signals.completed.connect(self.complete)
            worker.signals.started.connect(self.start)
            self.threadpool.start(worker)

    def live_view(self):
        self.imageViewer = pg.ImageView()

        self.LiveView = QtWidgets.QGroupBox()

        self.LiveViewButtonON = QtWidgets.QPushButton("Start Live View")
        self.LiveViewButtonUPDATE = QtWidgets.QPushButton("Update Live View")
        self.LiveViewButtonOFF = QtWidgets.QPushButton("Stop Live View")

        self.updateRateLV_label = QtWidgets.QLabel(
            "Live View Update Rates in Hz"
        )
        self.updateRateLV = QtWidgets.QComboBox()

        LVrates = [0.1, 0.2, 0.5, 1, 2, 5]
        self.updateRateLV.addItems([str(x) for x in LVrates])

        self.updateRateLV.setCurrentText("1")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.imageViewer, 0, 0, 10, 10)
        layout.addWidget(self.updateRateLV_label, 10, 3, 1, 1)
        layout.addWidget(self.updateRateLV, 10, 4, 1, 1)
        layout.addWidget(self.LiveViewButtonON, 11, 4, 1, 1)
        layout.addWidget(self.LiveViewButtonUPDATE, 11, 3, 1, 1)
        layout.addWidget(self.LiveViewButtonOFF, 11, 4, 1, 1)

        self.LiveViewButtonON.clicked.connect(self.set_live_view_status)

        self.LiveViewButtonON.clicked.connect(self.update_live_view)
        self.LiveViewButtonUPDATE.clicked.connect(self.update_live_view)
        self.LiveViewButtonOFF.clicked.connect(self.stop_live_view)

        self.LiveViewButtonOFF.setVisible(False)
        self.LiveViewButtonUPDATE.setVisible(False)

        self.LiveView.setLayout(layout)

    def set_live_view_status(self):
        self.live_view_on = not self.live_view_on

    def stop_live_view(self):
        self.LiveViewButtonOFF.setVisible(False)
        self.LiveViewButtonUPDATE.setVisible(False)
        self.LiveViewButtonON.setVisible(True)

        self.live_view_on = not self.live_view_on

    def update_live_view(self):
        self.LiveViewButtonOFF.setVisible(True)
        self.LiveViewButtonUPDATE.setVisible(True)
        self.LiveViewButtonON.setVisible(False)

        cmd = ["IMAGE", 0]

        self.LVworker = Queuer(
            cmd,
            self.camera_queue,
            1 / float(self.updateRateLV.currentText()),
            self.live_view_on,
        )

        self.LVworker.signals.completed.connect(self.complete)
        self.LVworker.signals.started.connect(self.start)

        self.LiveViewButtonOFF.clicked.connect(self.LVworker.stop)
        self.LiveViewButtonUPDATE.clicked.connect(self.LVworker.update)

        self.threadpool.start(self.LVworker)


class Sender(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    image = QtCore.pyqtSignal(np.ndarray)
    cmd_start = QtCore.pyqtSignal(list)
    cmd_end = QtCore.pyqtSignal(bool)

    def __init__(self, camera_queue, camera_obj, parent=None):
        super().__init__()
        self.queue = camera_queue
        self.camera = camera_obj

        self._running = True

    def run(self):
        while self._running:
            while not self.queue.empty():
                msg = self.queue.get()

                if msg[0] != "IMAGE":
                    self.cmd_start.emit([True, msg[0]])

                out = self.camera.messageHandler(msg)

                if msg[0] == "IMAGE":
                    try:
                        self.image.emit(out)
                    except RuntimeError:
                        pass
                else:
                    self.cmd_end.emit(out)

        try:
            self.finished.emit()
        except RuntimeError:
            pass

    def stop(self):
        self.finished.emit()
        self._running = False


class CommandStatus(QtWidgets.QDialog):
    def __init__(self, msg, parent=None):
        super(QtWidgets.QDialog, self).__init__(parent)

        self.label = QtWidgets.QLabel(f"Sending {msg} command")

        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.label, 0, 0)

        self.setLayout(layout)


class Signals(QtCore.QObject):
    started = QtCore.pyqtSignal(str)
    completed = QtCore.pyqtSignal(str)


class Queuer(QtCore.QRunnable):
    def __init__(self, cmd, queue, timeout, running=False):
        super(Queuer, self).__init__()

        self.msg = cmd
        self.timeout = timeout
        self.queue = queue
        self.signals = Signals()
        self._isRunning = running

    @QtCore.pyqtSlot()
    def run(self):
        while True:
            try:
                self.signals.started.emit(self.msg[0])
            except RuntimeError:
                pass

            self.queue.put(self.msg)

            if self.msg[0] == "IMAGE":
                time.sleep(self.timeout)

            else:
                time.sleep(self.timeout)

            if not self._isRunning:
                break

        try:
            self.signals.completed.emit(self.msg[0])
        except RuntimeError:
            pass

    def stop(self):
        self._isRunning = not self._isRunning

    def update(self):
        self._isRunning = True
