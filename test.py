import sour.sony as cam
import time

camera = cam.SONYconn(name='Sony RX0')

camera.initialize_camera(ControlMode='MediaTransfer')

camera.start_MTP_comms()

time.sleep(1.5)

files = camera.get_files_info()